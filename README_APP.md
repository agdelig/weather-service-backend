## Running with Docker  
First build the container and tag it appropriately.  
```buildoutcfg
docker build -t <tag_name> .
```

APPID provided by openweather.
```buildoutcfg
export APPID=<appid_provided by openweather>
```

One could also configure the environment the app is deployed on. there are two enviroment configurations.  
 * DEV (Debug mode turned on)
 * PROD
```buildoutcfg
export ENV=<DEV or PROD>
```

Run the container
```buildoutcfg
docker run -e APPID=$APPID -p 5000:5000 <tag_name>
```