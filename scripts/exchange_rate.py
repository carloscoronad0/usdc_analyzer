import requests
import json
import pandas as pd

YEARS = [y for y in range(2000, 2026)]

def clean_bcb_dolar_price_history(file):
    df = pd.read_excel(file, header=4)

    # Filter valid columns
    valid_columns = [col for col in df.columns if 'Unnamed' not in col]
    df = df[valid_columns]

    # Kept final values per month
    df = df[df['DIAS'] == 'PROM']
    df.dropna(inplace=True, axis=1)

    # Change months from columns to rows
    df = df.transpose().reset_index().drop(index=0)
    return df

def get_bcb_dolar_price_history(years):
    df_historico = pd.DataFrame()
    for year in years:
        response = requests.get(
            url=f"https://www.bcb.gob.bo/tiposDeCambioHistorico/xls.php?anio={year}"
        )

        if response.status_code == 200:
            file_name = f"./data/bcb/dolar_bob_price_history_{year}.xls"
            file = open(file_name, "wb")
            file.write(response.content)
            file.close()

            df = clean_bcb_dolar_price_history(file_name)
            df['YEAR'] = year
            df_historico = pd.concat([df_historico, df])
        else:
            print(f"{response.status_code}; {response.content}")

    df_historico.to_excel("./data/clean_dolar_bob_price_history.xlsx", index=False)

def get_usdc_dolar_price_history():
    with open("./data/usdt/usdt_bob_price_history.json", "r") as f:
        data = json.load(f)
        dates = data['categories']
        prices = data['items'][0]['values']
        df_history = pd.DataFrame(data={'dates': dates, 'prices': prices})

        df_history['dates'] = pd.to_datetime(df_history['dates'])
        df_history['YYYYMM'] = df_history['dates'].dt.strftime('%Y%m')
        df_grouped = df_history[['YYYYMM', 'prices']].groupby('YYYYMM').max().reset_index()

        df_grouped.to_excel("./data/clean_usdt_bob_monthly_price_history.xlsx", index=False)        
        df_history.to_excel("./data/clean_usdt_bob_daily_price_history.xlsx", index=False)        

get_usdc_dolar_price_history()
get_bcb_dolar_price_history(YEARS)