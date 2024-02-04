import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os


class Linear_QNet(nn.Module):
    def __init__(
        self, input_size, hidden_size, output_size, file_name="model.pth"
    ) -> None:
        self.model_folder_path = "./model"
        if not os.path.exists(self.model_folder_path):
            os.mkdir(self.model_folder_path)
        self.file_name = os.path.join(self.model_folder_path, file_name)
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self):
        torch.save(self.state_dict(), self.file_name)


class QTrainer:
    def __init__(self, model, lr, gamma) -> None:
        self.model = model
        if os.path.exists(model.model_folder_path):
            self.model.load_state_dict(torch.load(model.file_name))
            model.eval()
        self.lr = lr
        self.gamma = gamma
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.float)
        reward = torch.tensor(reward, dtype=torch.float)
        # (n , x); n for amount of batches most likley for long mem train

        if len(state.shape) == 1:
            # (1, x); 1 is number of batches for short mem train
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)

        # 1. predicted Q values with current state
        pred = self.model(state)  # Q_old

        # 2. find maximum next predicted Q value
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(
                    self.model(next_state[idx])
                )
            target[idx][torch.argmax(action).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()
