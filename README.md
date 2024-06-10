# SmartStride

SmartStride is a project designed to predict and analyze running speeds and inclinations using LSTM (Long Short-Term Memory) neural networks. This project includes training models for speed and inclination predictions based on historical data, and generating future predictions.

## Authors

Credits 

[Hirak Desai](https://www.github.com/hirak214)

[Yashvi Agrawal](https://github.com/yashviagrawal)

[Diya Hirani](https://github.com/DiyaHirani)


## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Model Training](#model-training)
- [Prediction Generation](#prediction-generation)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

SmartStride utilizes machine learning techniques to provide insights into running patterns. By analyzing past data on speed and inclination, the project aims to forecast future values, aiding runners in optimizing their performance and understanding their training progress.

## Features

- Data normalization for speed and inclination
- Sequence generation for LSTM model training
- LSTM model training for both speed and inclination prediction
- Model saving and loading for reuse
- Generation of future predictions based on trained models

## Installation

To install and set up the project, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/SmartStride.git
    cd SmartStride
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Ensure you have the necessary data in the appropriate format for training the models.

## Usage

### Training the Models

To train the models for speed and inclination prediction, run:

```bash
python train_models.py
