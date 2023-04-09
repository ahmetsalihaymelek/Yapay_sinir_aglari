# -*- coding: utf-8 -*-
"""5.1-5.2-5.3 Class.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/128hFthUFrPSQDhjcp57T38LN5ws4WaT2
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import datetime

from google.colab import drive
drive.mount("/content/drive")

firsTime=datetime.datetime.now()
print(firsTime)
torch.manual_seed(190401068)
batch_size = 16

# Veri setlerini yükleme
train_df = pd.read_csv('/content/drive/MyDrive/yapay_sinir_aglari/cure_the_princess_train.csv')
test_df = pd.read_csv('/content/drive/MyDrive/yapay_sinir_aglari/cure_the_princess_test.csv')
val_df = pd.read_csv('/content/drive/MyDrive/yapay_sinir_aglari/cure_the_princess_validation.csv')

from torch.utils.data import DataLoader, TensorDataset
train_inputs = train_df.drop('Cured', axis=1).values
train_labels = train_df['Cured'].values
train_dataset = TensorDataset(torch.tensor(train_inputs, dtype=torch.float), torch.tensor(train_labels, dtype=torch.long))

val_inputs = val_df.drop('Cured', axis=1).values
val_labels = val_df['Cured'].values
val_dataset = TensorDataset(torch.tensor(val_inputs, dtype=torch.float), torch.tensor(val_labels, dtype=torch.long))

test_inputs = test_df.drop('Cured', axis=1).values
test_labels = test_df['Cured'].values
test_dataset = TensorDataset(torch.tensor(test_inputs, dtype=torch.float), torch.tensor(test_labels, dtype=torch.long))

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size)
val_loader = DataLoader(val_dataset, batch_size=batch_size)

# Modeli oluşturma
class MLP(nn.Module):
    def __init__(self, input_size, hidden_size1, hidden_size2, output_size):
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size1)
        self.fc2 = nn.Linear(hidden_size1, hidden_size2)
        self.fc3 = nn.Linear(hidden_size2, output_size)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
       
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        out = self.relu(out)
        out = self.fc3(out)
        out = self.sigmoid(out)
        return out

# Model parametrelerini verme
input_size=len(train_df.columns) - 1
hidden_size1=100
hidden_size2=50
output_size=2

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = MLP(input_size, hidden_size1, hidden_size2, output_size).to(device)

#Optimizasyon için Stochastic Gradient Descent yöntemini seçilir
# Epoch sayısı ve learning rate değerlerini belirlenir
criterion=nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
num_epochs = 50

#######5.2#######
# Train ve validation döngüleri
train_loss_list=[]
val_loss_list=[]
best_val_loss=None
patience=5
for epoch in range(num_epochs):
    # Eğitim modu
    model.train()
    train_loss = 0.0
    correct = 0
    total = 0
    
    for data, target in train_loader:
        
        # Verileri tensörlere dönüştürün
        data, target = data.to(device), target.to(device)
        
        # Gradyanları sıfırlayın
        optimizer.zero_grad()
        
        # İleri doğru hesaplama
        output = model(data)
        #target= torch.flatten(target)
        loss = criterion(output, target)
        
        
        # Kaybı geriye doğru hesaplayın ve gradiyanları hesaplayın
        loss.backward()
        optimizer.step()
        
        # İstatistikleri takip edin
        train_loss += loss.item() * data.size(0)
        _, predicted = torch.max(output.data, 1)
        total += target.size(0)
        
        correct += (predicted == target).sum().item()
        
    
    train_loss /= len(train_loader.dataset)
    train_loss_list.append(train_loss)
    train_acc = 100 * correct / total
    
    # Değerlendirme modu
    model.eval()
    val_loss = 0.0
    
    
    with torch.no_grad():
        correct = 0
        total = 0
        for data, target in val_loader:
            data, target = data.to(device), target.to(device)
            
            # İleri doğru hesaplama
            output = model(data)
            loss = criterion(output, target)
            
            # İstatistikleri takip edin
            val_loss += loss.item() * data.size(0)
            _, predicted = torch.max(output.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
    
    val_loss /= len(val_loader.dataset)
    val_acc = 100 * (correct / total)
    val_loss_list.append(val_loss)
    #EarlyStopping
    val_score=val_loss
    # Her epok sonunda istatistikleri yazdırın
    print(f'Epoch: {epoch+1}/{num_epochs} - Train Loss: {train_loss:.4f} - Train Acc: {train_acc:.2f}% - Val Loss: {val_loss:.4f} - Val Acc: {val_acc:.2f}%')

import matplotlib.pyplot as plt

epochs = range(1, len(train_loss_list) + 1)
plt.plot(epochs, train_loss_list, 'b', label='Training loss')
plt.plot(epochs, val_loss_list, 'r', label='Validation loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

## Modelimiz Eğitim işlemlerini yukarda bitirdi ve en iyi modeli kaydetti kaydettiği bu modeli torch load ile birlikte boş bir modelin içine atayıp test verisi üzerinde deneme yapıcaz

input_size=len(train_df.columns) - 1
hidden_size1=100
hidden_size2=50
output_size=2

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#Farklı bir model adıyla oluşturdumki çalışıyormu görebileyim
model2 = MLP(input_size, hidden_size1, hidden_size2, output_size).to(device) #

model2.load_state_dict(torch.load("checkpoint.pt"))

######5-3#####
from sklearn.metrics import confusion_matrix

# Modeli değerlendirme modunda ayarla
model.eval()

# Test seti üzerinde döngüye gir ve tahminler yap
with torch.no_grad():
    true_labels = []
    predicted_labels = []
    for inputs, labels in test_loader:
        inputs = inputs.to(device)
        labels = labels.to(device)
        outputs = model2(inputs)
        _, predicted = torch.max(outputs.data, 1)
        true_labels += labels.cpu().numpy().tolist()
        predicted_labels += predicted.cpu().numpy().tolist()

# Confusion matrix'i hesapla
cm = confusion_matrix(true_labels, predicted_labels)

# Accuracy, precision, recall ve F1 skorlarını hesapla
accuracy = (cm.diagonal().sum()) / (cm.sum())
precision = (cm.diagonal() / cm.sum(axis=0)).mean()
recall = (cm.diagonal() / cm.sum(axis=1)).mean()
f1 = 2 * (precision * recall) / (precision + recall)
print("sadece model")
print(f"Test Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

lastTime=datetime.datetime.now()
print(f"Geçen süre{lastTime-firsTime} Device: {device}")

