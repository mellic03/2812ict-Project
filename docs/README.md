# Monocular Depth Estimation Demo


### Dependencies
All dependencies are listed in `requirements.txt` and can be installed through pip. It is recommended (but not required) that you use a virtual environment for this.
```    
$ pip3 install -r requirements.txt
```


### Calibration

![](hand-landmarks.png)

The main program will refuse to start before the calibration program has run. This is necessary as the proportions of the users hands and face need to be known for accurate depth estimation.

Run `calibration.py` from the root directory of the project. The program will first prompt for the real-world distance between hand landmarks 0 and 17. It will then request the expected real-world distance between the camera and the users face to be used during calibration.
```
$ python3 src/calibration.py
```

These only need to be rough measurements. For example, supplying a seating-depth of 1000mm but performing the calibration at 700mm is fine. The calibration program measures *proportions*, not absolute measurements.



### Demo Program
Run the main program
```
$ python3 src/main.py
```