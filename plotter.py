import matplotlib.pyplot as plt
from IPython import display

plt.ion()


def plot(scores, mean_scores, n_games):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title("Training...")
    plt.xlabel("Number of Games")
    plt.ylabel("Score")

    # Calculate the x-axis values starting from n_games
    x_values = list(range(n_games, n_games + len(scores)))

    plt.plot(x_values, scores, label="Scores")
    plt.plot(x_values, mean_scores, label="Mean Scores")

    plt.ylim(ymin=0)
    plt.text(x_values[-1], scores[-1], str(scores[-1]))
    plt.text(x_values[-1], mean_scores[-1], str(mean_scores[-1]))

    plt.legend()  # Add legend for clarity
    plt.show(block=False)
    plt.pause(0.1)
