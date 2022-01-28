import torch
import matplotlib.pyplot as plt

def generator(num=1000, save=True, visualize=True):
    a = torch.tensor(0.).normal_(0,10)
    b = torch.tensor(0.).uniform_(0,10)
    
    x = torch.arange(num).sub(num/2)
    x.mul_(a).add_(b)
    print(f'[AILEVER] A size-{num} tensor is created!')
    
    if save:
        # save : pth
        torch.save(x, f'tensor{num}.pth')
        print(f'[AILEVER] A size-{num} tensor is saved in the formmat-pth!')
        
        # save : txt
        with open(f'tensor{num}.txt', 'w') as f:
            f.write(str(x))
            print(f'[AILEVER] A size-{num} tensor is saved in the formmat-txt!')

    if visualize:
        y = x.numpy()
        plt.plot(y, lw=0, marker='x')
        plt.grid()
        # save : png
        plt.savefig(f'tensor{num}.png')
        plt.show()
        print(f'[AILEVER] A size-{num} tensor is visualized in the formmat-png!')
    
    return x.data

