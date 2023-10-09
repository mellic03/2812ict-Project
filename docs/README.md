# Monocular Depth Estimation Demo


### Dependencies
All dependencies are listed in `requirements.txt` and can be installed through pip. It is recommended (but not required) that you use a virtual environment for this.
```    
$ pip3 install -r requirements.txt
```


### Running the Demo

1. Before running the main program, the focal-length of the camera and the proportions of the user's hands and face have to be calculated. This is to provide accurate enough depth estimation.
Run `focal-length.py` from the root directory of the project.
    ```
    $ python3 src/focal-length.py
    ```

2. `focal-length.py` writes the data collected to `config/config.ini` which the main program can now read.
    ```
    $ python3 src/main.py
    ```