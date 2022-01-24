import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import init

def init_weights_1d(net, init_type='normal', gain=0.02):
    def init_func(m):
        classname = m.__class__.__name__
        if hasattr(m, 'weight') and (classname.find('Conv') != -1 or classname.find('Linear') != -1):
            if init_type == 'normal':
                init.normal_(m.weight.data, 0.0, gain)
            elif init_type == 'xavier':
                init.xavier_normal_(m.weight.data, gain=gain)
            elif init_type == 'kaiming':
                init.kaiming_normal_(m.weight.data, a=0, mode='fan_in')
            elif init_type == 'orthogonal':
                init.orthogonal_(m.weight.data, gain=gain)
            else:
                raise NotImplementedError('initialization method [%s] is not implemented' % init_type)
            if hasattr(m, 'bias') and m.bias is not None:
                init.constant_(m.bias.data, 0.0)
        elif classname.find('BatchNorm1d') != -1:
            init.normal_(m.weight.data, 1.0, gain)
            init.constant_(m.bias.data, 0.0)

    print('initialize network with %s' % init_type)
    net.apply(init_func)

class conv_block_1d(nn.Module):
    def __init__(self, ch_in, ch_out, batch_norm:bool=True, activation_fn=nn.ReLU):
        super().__init__()
        if batch_norm:
            self.conv = nn.Sequential(
                nn.Conv1d(ch_in, ch_out, kernel_size=3,stride=1,padding=1,bias=True),
                nn.BatchNorm1d(ch_out),
                activation_fn(inplace=True),
                nn.Conv1d(ch_out, ch_out, kernel_size=3,stride=1,padding=1,bias=True),
                nn.BatchNorm1d(ch_out),
                activation_fn(inplace=True)
            )       
        else:
            self.conv = nn.Sequential(
                nn.Conv1d(ch_in, ch_out, kernel_size=3,stride=1,padding=1,bias=True),
                activation_fn(inplace=True),
                nn.Conv1d(ch_out, ch_out, kernel_size=3,stride=1,padding=1,bias=True),
                activation_fn(inplace=True)
            )

    def forward(self,x):
        x = self.conv(x)
        return x

class up_conv_1d(nn.Module):
    def __init__(self, ch_in, ch_out, batch_norm:bool=True, activation_fn=nn.ReLU):
        super().__init__()
        if batch_norm:
            self.up = nn.Sequential(
                nn.Upsample(scale_factor=2),
                nn.Conv1d(ch_in,ch_out,kernel_size=3,stride=1,padding=1,bias=True),
		        nn.BatchNorm1d(ch_out),
			    activation_fn(inplace=True)
            )
        else:
            self.up = nn.Sequential(
                nn.Upsample(scale_factor=2),
                nn.Conv1d(ch_in,ch_out,kernel_size=3,stride=1,padding=1,bias=True),
			    activation_fn(inplace=True)
            )

    def forward(self,x):
        x = self.up(x)
        return x

class Recurrent_block_1d(nn.Module):
    def __init__(self, ch_out, t=2, batch_norm:bool=True, activation_fn=nn.ReLU):
        super().__init__()
        self.t = t
        self.ch_out = ch_out
        if batch_norm:
            self.conv = nn.Sequential(
                nn.Conv1d(ch_out,ch_out,kernel_size=3,stride=1,padding=1,bias=True),
	    	    nn.BatchNorm1d(ch_out),
			    activation_fn(inplace=True)
            )
        else:
            self.conv = nn.Sequential(
                nn.Conv1d(ch_out,ch_out,kernel_size=3,stride=1,padding=1,bias=True),
			    activation_fn(inplace=True)
            )

    def forward(self,x):
        for i in range(self.t):

            if i==0:
                x1 = self.conv(x)
            
            x1 = self.conv(x+x1)
        return x1
        
class RRCNN_block_1d(nn.Module):
    def __init__(self, ch_in, ch_out, t=2, batch_norm:bool=True, activation_fn=nn.ReLU):
        super().__init__()
        self.RCNN = nn.Sequential(
            Recurrent_block_1d(ch_out,t=t, batch_norm=batch_norm, activation_fn=activation_fn),
            Recurrent_block_1d(ch_out,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        )
        self.Conv_1x1 = nn.Conv1d(ch_in,ch_out,kernel_size=1,stride=1,padding=0)

    def forward(self,x):
        x = self.Conv_1x1(x)
        x1 = self.RCNN(x)
        return x+x1

class single_conv_1d(nn.Module):
    def __init__(self, ch_in, ch_out, batch_norm:bool=True, activation_fn=nn.ReLU):
        super().__init__()
        if batch_norm:
            self.conv = nn.Sequential(
                nn.Conv1d(ch_in, ch_out, kernel_size=3,stride=1,padding=1,bias=True),
                nn.BatchNorm1d(ch_out),
                activation_fn(inplace=True)
            )
        else:
            self.conv = nn.Sequential(
                nn.Conv1d(ch_in, ch_out, kernel_size=3,stride=1,padding=1,bias=True),
                activation_fn(inplace=True)
            )

    def forward(self,x):
        x = self.conv(x)
        return x

class Attention_block_1d(nn.Module):
    def __init__(self, F_g, F_l, F_int, batch_norm:bool=True, activation_fn=nn.ReLU):
        super().__init__()
        if batch_norm:
            self.W_g = nn.Sequential(
                nn.Conv1d(F_g, F_int, kernel_size=1,stride=1,padding=0,bias=True),
                nn.BatchNorm1d(F_int)
                )
            self.W_x = nn.Sequential(
                nn.Conv1d(F_l, F_int, kernel_size=1,stride=1,padding=0,bias=True),
                nn.BatchNorm1d(F_int)
            )
            self.psi = nn.Sequential(
                nn.Conv1d(F_int, 1, kernel_size=1,stride=1,padding=0,bias=True),
                nn.BatchNorm1d(1),
                nn.Sigmoid()
            )
        else:
            self.W_g = nn.Sequential(
                nn.Conv1d(F_g, F_int, kernel_size=1,stride=1,padding=0,bias=True),
                )
            self.W_x = nn.Sequential(
                nn.Conv1d(F_l, F_int, kernel_size=1,stride=1,padding=0,bias=True),
            )
            self.psi = nn.Sequential(
                nn.Conv1d(F_int, 1, kernel_size=1,stride=1,padding=0,bias=True),
                nn.Sigmoid()
            )
        
        self.relu = activation_fn(inplace=True)
        
    def forward(self,g,x):
        g1 = self.W_g(g)
        x1 = self.W_x(x)
        psi = self.relu(g1+x1)
        psi = self.psi(psi)

        return x*psi

class U_Net23_1D(nn.Module):
    def __init__(self, img_ch=3, output_ch=1, batch_norm:bool=True, hidden_activation_fn=nn.ReLU, ending_activation_fn=torch.tanh):
        super().__init__()
        self.out_fn = ending_activation_fn
        activation_fn = hidden_activation_fn
        self.Maxpool = nn.MaxPool1d(kernel_size=2,stride=2)

        self.Conv1 = conv_block_1d(ch_in=img_ch,ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv2 = conv_block_1d(ch_in=64,ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv3 = conv_block_1d(ch_in=128,ch_out=256, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv4 = conv_block_1d(ch_in=256,ch_out=512, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv5 = conv_block_1d(ch_in=512,ch_out=1024, batch_norm=batch_norm, activation_fn=activation_fn)

        self.Up5 = up_conv_1d(ch_in=1024,ch_out=512, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv5 = conv_block_1d(ch_in=1024, ch_out=512, batch_norm=batch_norm, activation_fn=activation_fn)

        self.Up4 = up_conv_1d(ch_in=512,ch_out=256, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv4 = conv_block_1d(ch_in=512, ch_out=256, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up3 = up_conv_1d(ch_in=256,ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv3 = conv_block_1d(ch_in=256, ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up2 = up_conv_1d(ch_in=128,ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv2 = conv_block_1d(ch_in=128, ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)

        self.Conv_1x1 = nn.Conv1d(64,output_ch,kernel_size=1,stride=1,padding=0)

    def forward(self,x):
        # encoding path
        x1 = self.Conv1(x)

        x2 = self.Maxpool(x1)
        x2 = self.Conv2(x2)
        
        x3 = self.Maxpool(x2)
        x3 = self.Conv3(x3)

        x4 = self.Maxpool(x3)
        x4 = self.Conv4(x4)

        x5 = self.Maxpool(x4)
        x5 = self.Conv5(x5)

        # decoding + concat path
        d5 = self.Up5(x5)
        d5 = torch.cat((x4, d5), dim=1)
        
        d5 = self.Up_conv5(d5)
        
        d4 = self.Up4(d5)
        d4 = torch.cat((x3, d4), dim=1)
        d4 = self.Up_conv4(d4)

        d3 = self.Up3(d4)
        d3 = torch.cat((x2, d3), dim=1)
        d3 = self.Up_conv3(d3)

        d2 = self.Up2(d3)
        d2 = torch.cat((x1, d2), dim=1)
        d2 = self.Up_conv2(d2)

        d1 = self.Conv_1x1(d2)
       
        if self.out_fn == None:
            return d1
        else:
            return self.out_fn(d1)

class U_Net18_1D(nn.Module):
    def __init__(self, img_ch=3, output_ch=1, batch_norm:bool=True, hidden_activation_fn=nn.ReLU, ending_activation_fn=torch.tanh):
        super().__init__()
        self.out_fn = ending_activation_fn
        activation_fn = hidden_activation_fn

        self.Maxpool = nn.MaxPool1d(kernel_size=2,stride=2)

        self.Conv1 = conv_block_1d(ch_in=img_ch,ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv2 = conv_block_1d(ch_in=64,ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv3 = conv_block_1d(ch_in=128,ch_out=256, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv4 = conv_block_1d(ch_in=256,ch_out=512, batch_norm=batch_norm, activation_fn=activation_fn)

        self.Up4 = up_conv_1d(ch_in=512,ch_out=256, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv4 = conv_block_1d(ch_in=512, ch_out=256, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up3 = up_conv_1d(ch_in=256,ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv3 = conv_block_1d(ch_in=256, ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up2 = up_conv_1d(ch_in=128,ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv2 = conv_block_1d(ch_in=128, ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)

        self.Conv_1x1 = nn.Conv1d(64,output_ch,kernel_size=1,stride=1,padding=0)

    def forward(self, x):
        # encoding path
        x1 = self.Conv1(x)

        x2 = self.Maxpool(x1)
        x2 = self.Conv2(x2)
        
        x3 = self.Maxpool(x2)
        x3 = self.Conv3(x3)

        x4 = self.Maxpool(x3)
        x4 = self.Conv4(x4)

        # decoding path
        d4 = self.Up4(x4)
        d4 = torch.cat((x3, d4), dim=1)
        d4 = self.Up_conv4(d4)

        d3 = self.Up3(d4)
        d3 = torch.cat((x2, d3), dim=1)
        d3 = self.Up_conv3(d3)

        d2 = self.Up2(d3)
        d2 = torch.cat((x1, d2), dim=1)
        d2 = self.Up_conv2(d2)

        d1 = self.Conv_1x1(d2)

        if self.out_fn == None:
            return d1
        else:
            return self.out_fn(d1)

class U_Net13_1D(nn.Module):
    def __init__(self, img_ch=3, output_ch=1, batch_norm:bool=True, hidden_activation_fn=nn.ReLU, ending_activation_fn=torch.tanh):
        super().__init__()
        self.out_fn = ending_activation_fn
        activation_fn = hidden_activation_fn

        self.Maxpool = nn.MaxPool1d(kernel_size=2,stride=2)

        self.Conv1 = conv_block_1d(ch_in=img_ch,ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv2 = conv_block_1d(ch_in=64,ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv3 = conv_block_1d(ch_in=128,ch_out=256, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up3 = up_conv_1d(ch_in=256,ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv3 = conv_block_1d(ch_in=256, ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up2 = up_conv_1d(ch_in=128,ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv2 = conv_block_1d(ch_in=128, ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)

        self.Conv_1x1 = nn.Conv1d(64,output_ch,kernel_size=1,stride=1,padding=0)

    def forward(self, x):
        # encoding path
        x1 = self.Conv1(x)

        x2 = self.Maxpool(x1)
        x2 = self.Conv2(x2)
        
        x3 = self.Maxpool(x2)
        x3 = self.Conv3(x3)

        d3 = self.Up3(x3)
        d3 = torch.cat((x2, d3), dim=1)
        d3 = self.Up_conv3(d3)

        d2 = self.Up2(d3)
        d2 = torch.cat((x1, d2), dim=1)
        d2 = self.Up_conv2(d2)

        d1 = self.Conv_1x1(d2)

        if self.out_fn == None:
            return d1
        else:
            return self.out_fn(d1)

class R2U_Net_1D(nn.Module):
    def __init__(self, img_ch=3, output_ch=1, t=2, batch_norm:bool=True, hidden_activation_fn=nn.ReLU, ending_activation_fn=torch.tanh):
        super().__init__()
        self.out_fn = ending_activation_fn
        activation_fn = hidden_activation_fn
        
        self.Maxpool = nn.MaxPool1d(kernel_size=2,stride=2)
        self.Upsample = nn.Upsample(scale_factor=2)

        self.RRCNN1 = RRCNN_block_1d(ch_in=img_ch,ch_out=64,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        self.RRCNN2 = RRCNN_block_1d(ch_in=64,ch_out=128,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        self.RRCNN3 = RRCNN_block_1d(ch_in=128,ch_out=256,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        self.RRCNN4 = RRCNN_block_1d(ch_in=256,ch_out=512,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        self.RRCNN5 = RRCNN_block_1d(ch_in=512,ch_out=1024,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        

        self.Up5 = up_conv_1d(ch_in=1024,ch_out=512, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_RRCNN5 = RRCNN_block_1d(ch_in=1024, ch_out=512,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up4 = up_conv_1d(ch_in=512,ch_out=256, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_RRCNN4 = RRCNN_block_1d(ch_in=512, ch_out=256,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up3 = up_conv_1d(ch_in=256,ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_RRCNN3 = RRCNN_block_1d(ch_in=256, ch_out=128,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up2 = up_conv_1d(ch_in=128,ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_RRCNN2 = RRCNN_block_1d(ch_in=128, ch_out=64,t=t, batch_norm=batch_norm, activation_fn=activation_fn)

        self.Conv_1x1 = nn.Conv1d(64,output_ch,kernel_size=1,stride=1,padding=0)


    def forward(self,x):
        # encoding path
        x1 = self.RRCNN1(x)

        x2 = self.Maxpool(x1)
        x2 = self.RRCNN2(x2)
        
        x3 = self.Maxpool(x2)
        x3 = self.RRCNN3(x3)

        x4 = self.Maxpool(x3)
        x4 = self.RRCNN4(x4)

        x5 = self.Maxpool(x4)
        x5 = self.RRCNN5(x5)

        # decoding + concat path
        d5 = self.Up5(x5)
        d5 = torch.cat((x4,d5),dim=1)
        d5 = self.Up_RRCNN5(d5)
        
        d4 = self.Up4(d5)
        d4 = torch.cat((x3,d4),dim=1)
        d4 = self.Up_RRCNN4(d4)

        d3 = self.Up3(d4)
        d3 = torch.cat((x2,d3),dim=1)
        d3 = self.Up_RRCNN3(d3)

        d2 = self.Up2(d3)
        d2 = torch.cat((x1,d2),dim=1)
        d2 = self.Up_RRCNN2(d2)

        d1 = self.Conv_1x1(d2)

        if self.out_fn == None:
            return d1
        else:
            return self.out_fn(d1)

class AttU_Net_1D(nn.Module):
    def __init__(self, img_ch=3, output_ch=1, batch_norm:bool=True, hidden_activation_fn=nn.ReLU, ending_activation_fn=torch.tanh):
        super().__init__()
        self.out_fn = ending_activation_fn
        activation_fn = hidden_activation_fn
        
        self.Maxpool = nn.MaxPool1d(kernel_size=2,stride=2)

        self.Conv1 = conv_block_1d(ch_in=img_ch,ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv2 = conv_block_1d(ch_in=64,ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv3 = conv_block_1d(ch_in=128,ch_out=256, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv4 = conv_block_1d(ch_in=256,ch_out=512, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Conv5 = conv_block_1d(ch_in=512,ch_out=1024, batch_norm=batch_norm, activation_fn=activation_fn)

        self.Up5 = up_conv_1d(ch_in=1024,ch_out=512, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Att5 = Attention_block_1d(F_g=512,F_l=512,F_int=256, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv5 = conv_block_1d(ch_in=1024, ch_out=512, batch_norm=batch_norm, activation_fn=activation_fn)

        self.Up4 = up_conv_1d(ch_in=512,ch_out=256, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Att4 = Attention_block_1d(F_g=256,F_l=256,F_int=128, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv4 = conv_block_1d(ch_in=512, ch_out=256, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up3 = up_conv_1d(ch_in=256,ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Att3 = Attention_block_1d(F_g=128,F_l=128,F_int=64, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv3 = conv_block_1d(ch_in=256, ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up2 = up_conv_1d(ch_in=128,ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Att2 = Attention_block_1d(F_g=64,F_l=64,F_int=32, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_conv2 = conv_block_1d(ch_in=128, ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)

        self.Conv_1x1 = nn.Conv1d(64,output_ch,kernel_size=1,stride=1,padding=0)

    def forward(self,x):
        # encoding path
        x1 = self.Conv1(x)

        x2 = self.Maxpool(x1)
        x2 = self.Conv2(x2)
        
        x3 = self.Maxpool(x2)
        x3 = self.Conv3(x3)

        x4 = self.Maxpool(x3)
        x4 = self.Conv4(x4)

        x5 = self.Maxpool(x4)
        x5 = self.Conv5(x5)

        # decoding + concat path
        d5 = self.Up5(x5)
        x4 = self.Att5(g=d5,x=x4)
        d5 = torch.cat((x4,d5),dim=1)        
        d5 = self.Up_conv5(d5)
        
        d4 = self.Up4(d5)
        x3 = self.Att4(g=d4,x=x3)
        d4 = torch.cat((x3,d4),dim=1)
        d4 = self.Up_conv4(d4)

        d3 = self.Up3(d4)
        x2 = self.Att3(g=d3,x=x2)
        d3 = torch.cat((x2,d3),dim=1)
        d3 = self.Up_conv3(d3)

        d2 = self.Up2(d3)
        x1 = self.Att2(g=d2,x=x1)
        d2 = torch.cat((x1,d2),dim=1)
        d2 = self.Up_conv2(d2)

        d1 = self.Conv_1x1(d2)
        
        if self.out_fn == None:
            return d1
        else:
            return self.out_fn(d1)

class R2AttU_Net_1D(nn.Module):
    def __init__(self, img_ch=3, output_ch=1, t=2, batch_norm:bool=True, hidden_activation_fn=nn.ReLU, ending_activation_fn=torch.tanh):
        super().__init__()
        self.out_fn = ending_activation_fn
        activation_fn = hidden_activation_fn
        
        self.Maxpool = nn.MaxPool1d(kernel_size=2,stride=2)
        self.Upsample = nn.Upsample(scale_factor=2)

        self.RRCNN1 = RRCNN_block_1d(ch_in=img_ch,ch_out=64,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        self.RRCNN2 = RRCNN_block_1d(ch_in=64,ch_out=128,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        self.RRCNN3 = RRCNN_block_1d(ch_in=128,ch_out=256,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        self.RRCNN4 = RRCNN_block_1d(ch_in=256,ch_out=512,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        self.RRCNN5 = RRCNN_block_1d(ch_in=512,ch_out=1024,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        

        self.Up5 = up_conv_1d(ch_in=1024,ch_out=512, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Att5 = Attention_block_1d(F_g=512,F_l=512,F_int=256, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_RRCNN5 = RRCNN_block_1d(ch_in=1024, ch_out=512,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up4 = up_conv_1d(ch_in=512,ch_out=256, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Att4 = Attention_block_1d(F_g=256,F_l=256,F_int=128, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_RRCNN4 = RRCNN_block_1d(ch_in=512, ch_out=256,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up3 = up_conv_1d(ch_in=256,ch_out=128, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Att3 = Attention_block_1d(F_g=128,F_l=128,F_int=64, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_RRCNN3 = RRCNN_block_1d(ch_in=256, ch_out=128,t=t, batch_norm=batch_norm, activation_fn=activation_fn)
        
        self.Up2 = up_conv_1d(ch_in=128,ch_out=64, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Att2 = Attention_block_1d(F_g=64,F_l=64,F_int=32, batch_norm=batch_norm, activation_fn=activation_fn)
        self.Up_RRCNN2 = RRCNN_block_1d(ch_in=128, ch_out=64,t=t, batch_norm=batch_norm, activation_fn=activation_fn)

        self.Conv_1x1 = nn.Conv1d(64,output_ch,kernel_size=1,stride=1,padding=0)


    def forward(self,x):
        # encoding path
        x1 = self.RRCNN1(x)

        x2 = self.Maxpool(x1)
        x2 = self.RRCNN2(x2)
        
        x3 = self.Maxpool(x2)
        x3 = self.RRCNN3(x3)

        x4 = self.Maxpool(x3)
        x4 = self.RRCNN4(x4)

        x5 = self.Maxpool(x4)
        x5 = self.RRCNN5(x5)

        # decoding + concat path
        d5 = self.Up5(x5)
        x4 = self.Att5(g=d5,x=x4)
        d5 = torch.cat((x4,d5),dim=1)
        d5 = self.Up_RRCNN5(d5)
        
        d4 = self.Up4(d5)
        x3 = self.Att4(g=d4,x=x3)
        d4 = torch.cat((x3,d4),dim=1)
        d4 = self.Up_RRCNN4(d4)

        d3 = self.Up3(d4)
        x2 = self.Att3(g=d3,x=x2)
        d3 = torch.cat((x2,d3),dim=1)
        d3 = self.Up_RRCNN3(d3)

        d2 = self.Up2(d3)
        x1 = self.Att2(g=d2,x=x1)
        d2 = torch.cat((x1,d2),dim=1)
        d2 = self.Up_RRCNN2(d2)

        d1 = self.Conv_1x1(d2)

        if self.out_fn == None:
            return d1
        else:
            return self.out_fn(d1)

class DoubleConv_1D(nn.Module):
    """(convolution => [BN] => ReLU) * 2"""
    def __init__(self, in_channels, out_channels, mid_channels=None, activation_function=nn.ReLU):
        super().__init__()
        if not mid_channels:
            mid_channels = out_channels
        self.double_conv = nn.Sequential(
            nn.Conv1d(in_channels, mid_channels, kernel_size=3, padding=1),
            nn.BatchNorm1d(mid_channels),
            activation_function(inplace=True),
            nn.Conv1d(mid_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm1d(out_channels),
            activation_function(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)

class OutConv_1D(nn.Module):
    def __init__(self, in_channels, out_channels, activation_function=torch.tanh):
        super().__init__()
        self.activation_function = activation_function
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        return self.activation_function(self.conv(x))

class Down_1D(nn.Module):
    """Downscaling with maxpool then double conv"""

    def __init__(self, in_channels, out_channels, activation_function=nn.ReLU):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool1d(2),
            DoubleConv_1D(in_channels, out_channels, None, activation_function=activation_function)
        )

    def forward(self, x):
        return self.maxpool_conv(x)

class Up_1D(nn.Module):
    """Upscaling then double conv"""

    def __init__(self, in_channels, out_channels, bilinear=False, activation_function=nn.ReLU):
        super().__init__()
        # if bilinear, use the normal convolutions to reduce the number of channels
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
            self.conv = DoubleConv_1D(in_channels, out_channels, in_channels // 2, activation_function=activation_function)
        else:
            self.up = nn.ConvTranspose1d(in_channels , in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv_1D(in_channels, out_channels, None, activation_function=activation_function)


    def forward(self, x1, x2):
        x1 = self.up(x1)
        # input is CHW
        #diffY = x2.size()[2] - x1.size()[2]
        #diffX = x2.size()[3] - x1.size()[3]

        #x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2, diffY // 2, diffY - diffY // 2])
        # if you have padding issues, see
        # https://github.com/HaiyongJiang/U-Net-Pytorch-Unstructured-Buggy/commit/0e854509c2cea854e247a9c615f175f76fbb2e3a
        # https://github.com/xiaopeng-liao/Pytorch-UNet/commit/8ebac70e633bac59fc22bb5195e513d5832fb3bd
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)

class ResBlock_1D(nn.Module):
    def __init__(self, in_channels, out_channels, identity_downsample=None, stride=1):
        super().__init__()
        self.expansion = 4
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size=1, stride=1, padding=0)
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=3, stride=stride, padding=1)
        self.bn2 = nn.BatchNorm1d(out_channels)
        self.conv3 = nn.Conv1d(out_channels, out_channels*self.expansion, kernel_size=1, stride=1, padding=0)
        self.bn3 = nn.BatchNorm1d(out_channels*self.expansion)
        self.relu = nn.ReLU()
        self.identity_downsample = identity_downsample
    
    def forward(self, x):
        identity = x
        
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)
        x = self.conv3(x)
        x = self.bn3(x)

        if self.identity_downsample is not None:
            identity = self.identity_downsample(identity)

        x += identity
        x = self.relu(x)
        return x

class ResNet_1D(nn.Module):
    def __init__(self, block, layers, image_channels, num_classes):
        super().__init__()
        self.in_channels = 64
        self.conv1 = nn.Conv1d(image_channels, 64, kernel_size=7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm1d(64)
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool1d(kernel_size=3, stride=2, padding=1)

        # Essentially the entire ResNet architecture are in these 4 lines below
        self.layer1 = self._make_layer(block, layers[0], intermediate_channels=64, stride=1)
        self.layer2 = self._make_layer(block, layers[1], intermediate_channels=128, stride=2)
        self.layer3 = self._make_layer(block, layers[2], intermediate_channels=256, stride=2)
        self.layer4 = self._make_layer(block, layers[3], intermediate_channels=512, stride=2)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        #x = self.avgpool(x)
        #x = x.reshape(x.shape[0], -1)
        #x = self.fc(x)

        return x

    def _make_layer(self, block, num_residual_blocks, intermediate_channels, stride):
        identity_downsample = None
        layers = []

        # Either if we half the input space for ex, 56x56 -> 28x28 (stride=2), or channels changes
        # we need to adapt the Identity (skip connection) so it will be able to be added
        # to the layer that's ahead
        if stride != 1 or self.in_channels != intermediate_channels * 4:
            identity_downsample = nn.Sequential(
                nn.Conv1d(self.in_channels, intermediate_channels * 4, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm1d(intermediate_channels * 4),
            )

        layers.append(block(self.in_channels, intermediate_channels, identity_downsample, stride))

        # The expansion size is always 4 for ResNet 50,101,152
        self.in_channels = intermediate_channels * 4

        # For example for first resnet layer: 256 will be mapped to 64 as intermediate layer,
        # then finally back to 256. Hence no identity downsample is needed, since stride = 1,
        # and also same amount of channels.
        for i in range(num_residual_blocks - 1):
            layers.append(block(self.in_channels, intermediate_channels))

        return nn.Sequential(*layers)

class ResUNet_1D(nn.Module):
    def __init__(self, block, layers, image_channels, num_classes):
        super().__init__()
        self.in_channels = 64
        self.conv1 = nn.Conv1d(image_channels, 64, kernel_size=7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm1d(64)
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool1d(kernel_size=3, stride=2, padding=1)

        self.doubleconv = DoubleConv_1D(image_channels,self.in_channels)

        # Essentially the entire ResNet architecture are in these 4 lines below
        self.layer1 = self._make_layer(block, layers[0], intermediate_channels=64, stride=1)
        self.layer2 = self._make_layer(block, layers[1], intermediate_channels=128, stride=2)
        self.layer3 = self._make_layer(block, layers[2], intermediate_channels=256, stride=2)
        self.layer4 = self._make_layer(block, layers[3], intermediate_channels=512, stride=2)
        self.up1 = Up_1D(2048, 1024)
        self.up2 = Up_1D(1024, 512)
        self.up3 = Up_1D(512, 256)
        #self.up4 = Up(256, 128)
        self.outc = OutConv_1D(256, num_classes)

        self.up4 = Up_1D(256, 128)

    def forward(self, input):
        x = input

        #x = self.conv1(x)
        #x = self.bn1(x)
        #x = self.relu(x)
        #x1 = self.maxpool(x)

        x1 = self.doubleconv(x)
        x2 = self.layer1(x1)
        x3 = self.layer2(x2)
        x4 = self.layer3(x3)
        x5 = self.layer4(x4)

        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        #x = self.up4(x, x1)
        x = self.outc(x)

        #x = self.avgpool(x)
        #x = x.reshape(x.shape[0], -1)
        #x = self.fc(x)

        return x

    def _make_layer(self, block, num_residual_blocks, intermediate_channels, stride):
        identity_downsample = None
        layers = []

        # Either if we half the input space for ex, 56x56 -> 28x28 (stride=2), or channels changes
        # we need to adapt the Identity (skip connection) so it will be able to be added
        # to the layer that's ahead
        if stride != 1 or self.in_channels != intermediate_channels * 4:
            identity_downsample = nn.Sequential(
                nn.Conv1d(self.in_channels, intermediate_channels * 4, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm1d(intermediate_channels * 4),
            )

        layers.append(block(self.in_channels, intermediate_channels, identity_downsample, stride))

        # The expansion size is always 4 for ResNet 50,101,152
        self.in_channels = intermediate_channels * 4

        # For example for first resnet layer: 256 will be mapped to 64 as intermediate layer,
        # then finally back to 256. Hence no identity downsample is needed, since stride = 1,
        # and also same amount of channels.
        for i in range(num_residual_blocks - 1):
            layers.append(block(self.in_channels, intermediate_channels))

        return nn.Sequential(*layers)

def ResNet50_1D(img_channel=3, num_classes=1000):
    return ResNet_1D(ResBlock_1D, [3, 4, 6, 3], img_channel, num_classes)

def ResNet101_1D(img_channel=3, num_classes=1000):
    return ResNet_1D(ResBlock_1D, [3, 4, 23, 3], img_channel, num_classes)

def ResNet152_1D(img_channel=3, num_classes=1000):
    return ResNet_1D(ResBlock_1D, [3, 8, 36, 3], img_channel, num_classes)

def ResUNet50_1D(img_channel=3, num_classes=1000):
    return ResUNet_1D(ResBlock_1D, [3, 4, 6, 3], img_channel, num_classes)

def ResUNet101_1D(img_channel=3, num_classes=1000):
    return ResUNet_1D(ResBlock_1D, [3, 4, 23, 3], img_channel, num_classes)

def ResUNet152_1D(img_channel=3, num_classes=1000):
    return ResUNet_1D(ResBlock_1D, [3, 8, 36, 3], img_channel, num_classes)

class AAM_1D(nn.Module):
    def __init__(self, in_ch,out_ch):
        super().__init__() 
        self.global_pooling = nn.AdaptiveAvgPool1d(1)

        self.conv1 = nn.Sequential(
            nn.Conv1d(in_ch, out_ch, 1, padding=0),
            nn.BatchNorm1d(out_ch),
            nn.ReLU(inplace=True))

        self.conv2 = nn.Sequential(
            nn.Conv1d(in_ch, out_ch, 1, padding=0),
            nn.BatchNorm1d(out_ch),
            nn.ReLU(inplace=True))

        self.conv3 = nn.Sequential(
            nn.Conv1d(out_ch, out_ch, 1, padding=0),
            nn.Softmax(dim=1))

        self.conv4 = nn.Sequential(
            nn.Conv1d(in_ch, out_ch, 1, padding=0),
            nn.BatchNorm1d(out_ch),
            nn.ReLU(inplace=True))

    def forward(self, input_high, input_low):
        mid_high=self.global_pooling(input_high)
        weight_high=self.conv1(mid_high)

        mid_low = self.global_pooling(input_low)
        weight_low = self.conv2(mid_low)

        weight=self.conv3(weight_low+weight_high)
        low = self.conv4(input_low)
        return input_high+low.mul(weight)

class RAUNet_1D(nn.Module):
    def __init__(self, num_classes=1, num_channels=3, pretrained=True):
        super().__init__()
        #assert num_channels == 3
        self.w = 512
        self.h = 640
        self.num_classes = num_classes
        # filters = [64, 128, 256, 512]
        # resnet = models.resnet34(pretrained=pretrained)
        filters = [256, 512, 1024, 2048]
        # resnet = models.resnet50(pretrained=pretrained)
        resnet = ResUNet50_1D(num_channels, num_classes=num_classes)

        self.firstconv = resnet.conv1
        self.firstbn = resnet.bn1
        self.firstrelu = resnet.relu
        self.firstmaxpool = resnet.maxpool
        self.encoder1 = resnet.layer1
        self.encoder2 = resnet.layer2
        self.encoder3 = resnet.layer3
        self.encoder4 = resnet.layer4

        # Decoder
        self.decoder4 = DecoderBlockLinkNet_1D(filters[3], filters[2])
        self.decoder3 = DecoderBlockLinkNet_1D(filters[2], filters[1])
        self.decoder2 = DecoderBlockLinkNet_1D(filters[1], filters[0])
        self.decoder1 = DecoderBlockLinkNet_1D(filters[0], filters[0])
        self.gau3 = AAM_1D(filters[2], filters[2]) #RAUNet
        self.gau2 = AAM_1D(filters[1], filters[1])
        self.gau1 = AAM_1D(filters[0], filters[0])


        # Final Classifier
        self.finaldeconv1 = nn.ConvTranspose1d(filters[0], 32, 3, stride=2)
        self.finalrelu1 = nn.ReLU(inplace=True)
        self.finalconv2 = nn.Conv1d(32, 32, 3)
        self.finalrelu2 = nn.ReLU(inplace=True)
        self.finalconv3 = nn.Conv1d(32, num_classes, 2, padding=1)
        self.tanh = nn.Tanh()

    # noinspection PyCallingNonCallable
    def forward(self, x):
        # Encoder
        x = self.firstconv(x)
        x = self.firstbn(x)
        x = self.firstrelu(x)
        x = self.firstmaxpool(x)
        e1 = self.encoder1(x)
        e2 = self.encoder2(e1)
        e3 = self.encoder3(e2)
        e4 = self.encoder4(e3)

        d4 = self.decoder4(e4)
        b4 = self.gau3(d4, e3)
        d3 = self.decoder3(b4)
        b3 = self.gau2(d3, e2)
        d2 = self.decoder2(b3)
        b2 = self.gau1(d2, e1)
        d1 = self.decoder1(b2)

        # Final Classification
        f1 = self.finaldeconv1(d1)
        f2 = self.finalrelu1(f1)
        f3 = self.finalconv2(f2)
        f4 = self.finalrelu2(f3)
        f5 = self.finalconv3(f4)

        if self.num_classes > 1:
            x_out = torch.log_softmax(f5, dim=1)
        else:
            x_out = f5
        return self.tanh(x_out)
        
class DecoderBlockLinkNet_1D(nn.Module):
    def __init__(self, in_channels, n_filters):
        super().__init__()

        self.relu = nn.ReLU(inplace=True)
        self.conv1 = nn.Conv1d(in_channels, in_channels // 4, 1)
        self.norm1 = nn.BatchNorm1d(in_channels // 4)

        # B, C/4, H, W -> B, C/4, 2 * H, 2 * W
        self.deconv2 = nn.ConvTranspose1d(in_channels // 4, in_channels // 4, kernel_size=4, stride=2, padding=1, output_padding=0)
        self.norm2 = nn.BatchNorm1d(in_channels // 4)

        # B, C/4, H, W -> B, C, H, W
        self.conv3 = nn.Conv1d(in_channels // 4, n_filters, 1)
        self.norm3 = nn.BatchNorm1d(n_filters)


    def forward(self, x):
        x = self.conv1(x)
        x = self.norm1(x)
        x = self.relu(x)
        x = self.deconv2(x)
        x = self.norm2(x)
        x = self.relu(x)
        x = self.conv3(x)
        x = self.norm3(x)
        x = self.relu(x)
        return x
