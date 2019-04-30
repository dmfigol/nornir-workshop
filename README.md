# Jupyter notebooks for Nornir workshop
To be able to run the notebook, you need to have Docker and make installed.  
Also, you need some IOS/IOS-XE devices in your environment. Change `jupyter/inventory/hosts.yaml` accordingly.  
To start the container, run:  
`make up`
Then open `http://localhost:58888/` in the browser and open `workshop.ipynb`.  
To stop the container, run:  
`make stop`