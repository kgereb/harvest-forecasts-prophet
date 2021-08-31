# harvest-forecasts-prophet

This app was created for the Melbourne Datathon in 2019, forecasting sugar cane yields and time to harvest periods based on Sentinel-2 satellite images. The app was deployed with heroku, access the app here:
https://datathon2019-sentinel2.herokuapp.com/

## Requirements 

A Python 3.7.1 virtual environment was created for the app, necessary libraries are in `requirements.txt`. After installation, the app can be run locally as:

python app.py


## Analysis

Satellite images in different bands were provided to the teams. Masks for the sugarcane fields were provided, so we could apply these masks to identify the correct fields.  

Cloud coverage had to be dealt with during the image processing steps. My team created hand-labelled images in the different bands to identify clouds and uncovered fields, and built a classification ML model to predict cloud coverage.    

Next, we used the images in different bands to derive colors (NDVI, WDRVI, GRVI, GNVDI), measured as the difference between pixel values in different bands. 

Colors do change over the months as crops grow, following a cyclic pattern. My personal contribution was to use Facebook's Prophet to fit a forecasting model to these cycles and predict time to harvest periods and crop yields. The Prophet code is in `/create_tte_data/prophet_predictions.py`.

The time of harvest was visually determined by inspecting the images, and sugarcane yields were estimated based on the size of the fields as measured from the satellite images (knwoing the image resolution). 


## A Screenshot of the app

![App](https://github.com/kgereb/harvest-forecasts-prophet/blob/main/app.png)
