# Coastal Tools

### Description
The Coastal tools repo provides functions to set up coastal hydrologic models using NOAA/Enterprise Hydrofabric data. One of this repo is the connection to remote s3 buckets through the usage of HydroMT data catalogs. 

### Supported Coastal Models:
- [SFINCS](https://sfincs.readthedocs.io/en/latest/index.html)
    - SFINCS is a reduced-complexity model created by Deltares
    - Many of the SFINCS_builder.py functions included in coastal-tools are wrapper functions around Deltares' [HydroMT-SFINCS](https://deltares.github.io/hydromt_sfincs/stable/) Library

### Getting started
To run the tools in this repo:
```sh
git clone https://github.com/taddyb/coastal-tools.git
cd coastal-tools
pip install -e .
```
*This assumes you have created a virtual env for your package management*

### Running tests
Tests of the initial parameters functions are run on the LowerColorado domain (the same area that [T-Route](https://github.com/NOAA-OWP/t-route) uses) and can be executed through the following 
```sh
pip install -e .[test]
pytest
```

### Running example notebooks
A full visualization walk through of the LowerColordo test case can be found in the example notebook
```sh
pip install -e .[jupyter]
```
