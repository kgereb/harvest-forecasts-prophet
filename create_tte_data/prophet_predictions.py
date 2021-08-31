import pandas as pd
from fbprophet import Prophet


df = pd.read_csv('NDVI_series.csv')


# Predict sales using Prophet for each group separately
def make_prophet_forecast(mydf, prediction_intervals):
    """
    Take in training data (df) and use it to forecast into the future (according to prediction_intervals).
    """

    m_prophet = Prophet(daily_seasonality=True)
    m_prophet.add_seasonality(name='yearly', period=365, fourier_order=5)

    # Fit model
    m_prophet.fit(mydf)
    # Predict the future
    # Specify the range of days we are forecasting for, including historical data
    prophet_forecast_df = m_prophet.make_future_dataframe(periods=prediction_intervals, include_history=True)    
    prophet_forecast_df = m_prophet.predict(prophet_forecast_df)
    
    return prophet_forecast_df[['ds','yhat']]

        
def get_pred_df(field_nr, mydf):
    
        mydata = mydf[mydf['field_ID']==field_nr][['date', 'NDVI']]
        # Rename columns based on what prophet expects|
        mydata = mydata.rename(columns={'date': 'ds', 'NDVI': 'y'})

        PREDICTION_LENGTH = 400
        pred_prophet = make_prophet_forecast(mydata, PREDICTION_LENGTH)
        pred_prophet['field_ID'] = pred_prophet.apply(lambda x: field_nr, axis=1)

        return pred_prophet 

    
pred_df = get_pred_df(1, df)
for i in range(2, df['field_ID'].nunique()+1):
     pred_df  = pd.concat([pred_df, get_pred_df(i, df)])
     print(i)
    
pred_df.to_csv('Prophet_NDVI_preds.csv')        