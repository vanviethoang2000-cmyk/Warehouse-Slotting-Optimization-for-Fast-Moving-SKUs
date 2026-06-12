# Warehouse-Slotting-Optimization-for-Fast-Moving-SKUs

This project focuses on warehouse data analysis, slotting simulation, and SKU demand forecasting.

## 1. Objectives

* Organize data and source code in a clear structure for easier maintenance.
* Process data, extract features, and cluster SKUs.
* Build a warehouse slotting model/logic.
* Save report results, images, and data for the dashboard.

## 2. Folder Structure

```text
Project_finals/
|-- data/
|   |-- raw/
|   |   `-- raw_data.xlsx
|   `-- processed/
|-- features/
|-- notebooks/
|-- src/
|   |-- envs/
|   |   `-- warehouse_env.py
|   |-- features/
|   |-- forecasts/
|   |-- models/
|   |   |-- simulation_model.py
|   |   `-- slotting_algorithms.py
|   |-- outputs/
|   |   |-- figures/
|   |   |-- images/
|   |   |-- powerbi/
|   |   `-- reports/
|   |-- sql/
|   `-- utils/
|-- dashboard/
|-- docs/
|-- .gitignore
|-- requirements.txt
`-- Untitled-1.ipynb
```

## 3. Environment Setup

### Option 1: Using venv (recommended)

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Option 2: If an environment is already available

Simply activate the environment and install the dependencies:

```powershell
pip install -r requirements.txt
```

## 4. Main Libraries

* pandas, numpy
* scikit-learn, xgboost, lightgbm
* matplotlib, seaborn, plotly
* notebook, ipykernel
* streamlit, openpyxl
* tensorflow, tqdm, kaleido

## 5. Suggested Workflow

1. Place the original data file in the `data/raw` folder.
2. Perform preprocessing and create the processed dataset.
3. Run the notebooks in the `notebooks` folder or the original notebook for feature engineering.
4. Run the modules in `src/models` to simulate slotting and evaluate the results.
5. Save the outputs to `src/outputs` and use them for the dashboard.

## 6. Notes

* Avoid committing large raw data files and temporary files.
* Documentation in the `docs` folder should be updated when the processing logic changes.
* Additional README files can be added for each module in `src` if the project expands.
