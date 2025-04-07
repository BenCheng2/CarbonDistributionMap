## 1. The procedure to duplicate the baseline distribution graph: 
1. （Optional) Create venv python environment
2. Install dependencies: pip install -r requirements.txt
3. Open /lab/lab3.ipynb with any software supporting Jupyter Notebook
4. Run the notebook

## 2. Duplicate the morning distribution graph:
1. Open /helpers/DataLoader.py
2. Find
```
    # Morning (24 Hour)
    # self.generator_supply_df = pd.read_csv("../data/timeseries/local/GeneratorSupply_20250405_0801.csv")
```
3. Uncomment the line above
4. Follow exactly the same steps as in (**1**) to run the notebook

## 3. Duplicate the evening distribution graph:
1. Open /helpers/DataLoader.py
2. Find
```
    # Evening (24 Hour)
    # self.generator_supply_df = pd.read_csv("../data/timeseries/local/GeneratorSupply_20250405_2004.csv")
```
3. Uncomment the line above
4. Follow exactly the same steps as in (**1**) to run the notebook

## 4. (Optional) Duplicate the anytime distribution graph:
1. Open /helpers/DataLoader.py
2. Find
```
    # Evening (24 Hour)
    # self.generator_supply_df = pd.read_csv("../data/timeseries/local/GeneratorSupply_20250405_2004.csv")
```
3. Follow the exact text style and change the file path to the target file
4. Follow exactly the same steps as in (**1**) to run the notebook

## 5. Duplicate Timeseries graph:
1. Open /lab/timeseries.ipynb
2. Execute the notebook

## 6. Double Check Vector Similarity between population and hourly load
1. Open /lab/VectorSimilarityComparison.ipynb
2. Execute the notebook

## 7. Change the year of the hourly load data
1. Open /lab/lab3.ipynb
2. Search for the line
```
    year = 2021
```
3. Change the year to the target year
4. Restart the kernel and run the notebook

## 8. Duplicate City Border Visualization with Color
1. Open /lab/AdditionalVisualization.ipynb
2. Execute the notebook
3. 
## 9. Duplicate the QGIS visualization
1. Open /data/qgis
2. .shp files conatains the spatial data for different layers
3. .qgs files contains the main QGIS project information
4. Install Freehand Raster Georeferencer plugin
5. Open .qgs file with QGIS software, the shapefiles will be loaded automatically
