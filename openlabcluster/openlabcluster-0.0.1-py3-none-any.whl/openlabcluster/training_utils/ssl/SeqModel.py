# load file
import torch
import torch.nn as nn
from openlabcluster.training_utils.ssl.EnDeModel import EncoderRNN, DecoderRNN, Classification

class seq2seq(nn.Module):
    def __init__(self, en_input_size, en_hidden_size, output_size, batch_size,
                 en_num_layers=3, de_num_layers=1,
                 fix_state=False, fix_weight=False, teacher_force=False, device = 'cuda'):
        super(seq2seq, self).__init__()
        self.batch_size = batch_size
        self.en_num_layers = en_num_layers
        self.device = device
        self.encoder = EncoderRNN(en_input_size, en_hidden_size, en_num_layers, device).to(self.device)
        self.decoder = DecoderRNN(output_size, en_hidden_size * 2, de_num_layers).to(self.device)
        self.fix_state = fix_state
        self.fix_weight = fix_weight

        if self.fix_weight:
            with torch.no_grad():
                # decoder fix weight
                self.decoder.gru.requires_grad = False
                self.decoder.out.requires_grad = False

        self.en_input_size = en_input_size
        self.teacher_force = teacher_force

    def forward(self, input_tensor, seq_len):
        self.batch_size = len(seq_len)

        encoder_hidden = self.encoder(
            input_tensor, seq_len)

        # tmp = encoder_hidden.view(self.en_num_layers, 2, batch_size, encoder.hidden_size)
        # decoder_hidden = torch.cat((tmp[self.en_num_layers-1:self.en_num_layers,0,:,:],
        #                             tmp[encoder.num_layers-1:encoder.num_layers,1,:,:]), 2)

        decoder_output = torch.Tensor().to(self.device)
        # decoder_hidden = encoder_hidden  # torch.empty((1,len(seq_len), out_seq.shape[-1]))
        # decoder part
        if self.teacher_force:
            de_input = torch.zeros([self.batch_size, 1, self.en_input_size], dtype=torch.float)
            de_input = torch.cat((de_input, input_tensor[:, 1:, :]), dim=1).to(self.device)
        else:
            de_input = torch.zeros(input_tensor.size(), dtype=torch.float).to(self.device)

        if self.fix_state:
            # de_input = torch.zeros([self.batch_size, 1, self.en_input_size], dtype=torch.float).to(device)

            # for it in range(max(seq_len)):
            #     deout_tmp, _ = self.decoder(
            #         de_input[:,it:it+1], encoder_hidden)
            #     decoder_output = torch.cat((decoder_output, deout_tmp), dim=1)

            de_input = input_tensor[:, 0:1,
                       :]  # torch.zeros([self.batch_size, 1, self.en_input_size], dtype=torch.float).to(device)

            for it in range(max(seq_len)):
                deout_tmp, _ = self.decoder(
                    de_input, encoder_hidden)
                deout_tmp = deout_tmp + de_input
                de_input = deout_tmp
                decoder_output = torch.cat((decoder_output, deout_tmp), dim=1)
        else:
            hidden = encoder_hidden
            for it in range(max(seq_len)):
                deout_tmp, hidden = self.decoder(
                    de_input[:, it:it + 1, :], hidden)

                decoder_output = torch.cat((decoder_output, deout_tmp), dim=1)
            # else:
            #     de_input = torch.zeros([self.batch_size, 1, self.en_input_size], dtype=torch.float).to(device)
            #     deout_tmp, hidden = self.decoder(
            #         de_input, hidden)
            #     for it in range(max(seq_len)):
            #         deout_tmp, hidden = self.decoder(
            #             de_input, hidden)
            #         #de_input = deout_tmp
            #         decoder_output = torch.cat((decoder_output, deout_tmp), dim=1)
        return encoder_hidden, decoder_output

class SemiSeq2Seq(nn.Module):
    def __init__(self, en_input_size, en_hidden_size, output_size, batch_size, cla_dim,
                 en_num_layers=3, de_num_layers=1, cl_num_layers=1,
                 fix_state=False, fix_weight=False, teacher_force=False, device='cuda'):
        super(SemiSeq2Seq, self).__init__()

        self.seq = seq2seq(en_input_size, en_hidden_size, output_size, batch_size,
                           en_num_layers=en_num_layers, de_num_layers=de_num_layers,
                           fix_state=fix_state, fix_weight=fix_weight, teacher_force=teacher_force, device=device)
        self.classifier = Classification(en_hidden_size * 2, cla_dim, cl_num_layers, device)

    def forward(self, input_tensor, seq_len):
        encoder_hidden, deout = self.seq(input_tensor, seq_len)
        pred, inter = self.classifier(encoder_hidden[0, :, :])

        # return encoder_hidden, deout, pred
        return inter, deout, pred



