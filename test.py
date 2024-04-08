# Load the synthetic data with date
data = pd.read_csv('synth_run_data_single_user.csv', parse_dates=['timestamp'])

# Feature Engineering
data['hour_of_day'] = data['timestamp'].dt.hour
data['day_of_week'] = data['timestamp'].dt.dayofweek
data['month'] = data['timestamp'].dt.month
data['time_of_day'] = pd.cut(data['hour_of_day'], bins=[0, 6, 12, 18, 24], labels=[0, 1, 2, 3])

# Running Metrics
data['average_speed'] = data.groupby('timestamp')['speed'].transform('mean')
data['max_speed'] = data.groupby('timestamp')['speed'].transform('max')
data['min_speed'] = data.groupby('timestamp')['speed'].transform('min')
data['speed_trend'] = data['speed'].rolling(window=10, min_periods=1).mean()

# Additional Derived Features
data['progress_towards_target'] = data['current_weight'] - data['target_weight']
data['speed_change'] = data['speed'].diff()

# Select relevant features for model training
features = ['age', 'height', 'current_weight', 'weeks_to_achieve', 'day_of_week', 'month', 'time_of_day', 'average_speed', 'max_speed', 'min_speed', 'speed_trend', 'progress_towards_target', 'speed_change']

# Drop unnecessary columns
data = data[features + ['speed']]  # Ensure target variable is included

# Print column names before one-hot encoding
print("Before one-hot encoding:", data.columns.tolist())

# Split data into features and target variable
X = data[features]
y = data['speed']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)


# Load your dataset (replace 'your_dataset.csv' with your actual dataset)
df = pd.read_csv('synth_run_data_single_user.csv')

# Assuming the dataset has columns 'timestamp' and 'speed'
# For simplicity, you might need to include other features based on your dataset

# Convert 'timestamp' to datetime and set it as the index
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.set_index('timestamp')

# Normalize the 'speed' column
scaler = MinMaxScaler()
df['speed_normalized'] = scaler.fit_transform(df[['speed']])

# Function to create sequences for LSTM
def create_sequences(data, sequence_length):
    sequences = []
    targets = []
    for i in range(len(data) - sequence_length):
        seq = data.iloc[i:i+sequence_length]['speed_normalized']
        target = data.iloc[i+sequence_length]['speed_normalized']
        sequences.append(seq.values)
        targets.append(target)
    return np.array(sequences), np.array(targets)

# Define the sequence length (adjust based on your requirement)
sequence_length = 10

# Create sequences and targets
sequences, targets = create_sequences(df[['speed_normalized']], sequence_length)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(sequences, targets, test_size=0.2, random_state=42)

# Reshape the data to fit the LSTM model input shape
X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

# Build the LSTM model
model = Sequential()
model.add(LSTM(50, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

# Now, you can use the trained model to generate a new run based on the past data.
# You need to create a sequence similar to the training sequences and predict the next value.

# For simplicity, let's use the last sequence from the testing data to generate a new run
new_sequence = X_test[-1].reshape(1, sequence_length, 1)
predicted_speed_normalized = model.predict(new_sequence)

# Inverse transform to get the predicted speed in the original scale
predicted_speed = scaler.inverse_transform(predicted_speed_normalized.reshape(-1, 1))

# Print the predicted speed for the next time step
print("Predicted Speed for the Next Time Step:", predicted_speed[0, 0])

# Initialize the initial sequence with the last sequence from the testing data
generated_sequence = X_test[-1].reshape(1, sequence_length, 1)

# Number of time steps to generate
num_time_steps = 100

# Initialize a list to store the generated speed values
generated_speed_values = []

# Generate the time series data
for _ in range(num_time_steps):
    # Predict the next speed value
    predicted_speed_normalized = model.predict(generated_sequence)
    
    # Inverse transform to get the predicted speed in the original scale
    predicted_speed = scaler.inverse_transform(predicted_speed_normalized.reshape(-1, 1))
    
    # Append the predicted speed to the generated sequence
    generated_sequence = np.append(generated_sequence[:, 1:, :], predicted_speed_normalized.reshape(1, 1, 1), axis=1)
    
    # Append the predicted speed to the list
    generated_speed_values.append(predicted_speed[0, 0])

# Create a time index for the generated time series
generated_time_index = pd.date_range(start=df.index[-1] + pd.Timedelta(minutes=5), periods=num_time_steps, freq='5s')

# Create a DataFrame for the generated time series
generated_time_series = pd.DataFrame({'timestamp': generated_time_index, 'predicted_speed': generated_speed_values})


# Plot the generated time series
plt.figure(figsize=(12, 6))
plt.plot(generated_time_series['timestamp'], generated_time_series['predicted_speed'], label='Generated Time Series', color='red')
plt.title('Generated Time Series')
plt.xlabel('Timestamp')
plt.ylabel('Speed (km/hr)')
plt.legend()
plt.show()
