from .infer import *
import nnresample
from .timestamp_generator import extract_time_stamps
# import gradio as gr

import time


def wav_to_pcm16(wav):
    ints = (wav * 32768).astype(np.int16)
    little_endian = ints.astype('<u2')
    wav_bytes = little_endian.tobytes()
    return wav_bytes


def infer_using_vad_chunks(wav_file):
    t1 = time.time()
    signal, sr = sf.read(wav_file.name)
    signal = signal.mean(-1)
    resampled_signal = nnresample.resample(signal, 16000, 44100)
    
    wav_bytes = wav_to_pcm16(resampled_signal)
    start_times, end_times = extract_time_stamps(wav_bytes)
    stt_output = []

    for i in range(len(start_times)):
        chunk = resampled_signal[int(start_times[i]*16000): int(end_times[i]*16000)]
        result = wav2vec_obj.get_results(wav_path=chunk, use_cuda=True)        
        stt_output.append(result)

    asr_result = ' '.join(stt_output)
    #itn_result = inverse_normalize_text([asr_result], lang='hi')
    '''
    t2 = time.time()
    r_2_punct = requests.post(url='https://13870.gradio.app/api/predict', json={"data": [asr_result]})
    punct_en_text = r_2_punct.json()['data'][0]
    t3 = time.time()
    r_3_trans = requests.post(url='https://36474.gradio.app/api/predict', json={"data": [punct_en_text]})
    translated_text = r_3_trans.json()['data'][0]
    t4 = time.time()
    r_4_tts = requests.post(url='https://22915.gradio.app/api/predict', json={"data": [translated_text]})
    
    tts_result_wav = r_4_tts.json()['data'][0].split(',')[-1]
    t5 = time.time()
    # file_name = "wav_files/temp.wav"
    # wav_file = open(file_name, "wb")
    decode_string = base64.b64decode(tts_result_wav)
    sr, data_npy = read(io.BytesIO(decode_string))
    
    # wav_file.write(decode_string)
    t6 = time.time()
    '''
    # with open('./time.txt', 'a+') as f:
    #     f.write(f'\n*********\nNum chars: {len(asr_result)}\nASR: {(t2-t1)*1000:.2f}\n Punct: {(t3-t2)*1000:.2f}\n Trans: {(t4-t3)*1000:.2f}\n TTS: {(t5-t4)*1000:.2f}\n File writing: {(t6-t5)*1000:.2f}')
    return asr_result #, punct_en_text, translated_text, (sr, data_npy)

def run_gradio():
    audio = gr.inputs.Audio(source="microphone", type="file")
    #output = [gr.outputs.Textbox(label="Speech to Text"), gr.outputs.Textbox(label="Punctuation"), gr.outputs.Textbox(label="Translation"), gr.outputs.Audio(type="numpy", label="TTS")]
    output = gr.outputs.Textbox(label="STT") #, gr.outputs.Textbox("ITN")]
    iface = gr.Interface(fn=infer_using_vad_chunks, inputs=audio, outputs=output,
            server_port=8888, server_name="0.0.0.0", enable_queue=True, theme='huggingface', layout='vertical', title='Speech to Text: Hi')

    iface.launch(share=True)

def load_model_and_dependencies(model, dict, decoder, cuda=False, half=False, lexicon=False, lm_path=False):
    target_dict = Dictionary.load(dict)
    print("Model Loaded")
    model = get_model(cuda, model, half)
    print("Generator Loaded")
    generator = get_decoder(target_dict, decoder, lexicon, lm_path)

    cuda = cuda
    wav2vec_obj = customWav2vec(model, target_dict, generator, args_local.half)
    return wav2vec_obj

if __name__ == "__main__":
    global wav2vec_obj, cuda
    parser = argparse.ArgumentParser(description='Run')
    parser.add_argument('-m', '--model', type=str, help="Custom model path")
    parser.add_argument('-d', '--dict', type=str, help="Dict path")
    parser.add_argument('-w', '--wav', type=str, help= "Wav file path")
    parser.add_argument('-c', '--cuda', default=False, type=bool, help="CUDA True or False")
    parser.add_argument('-D', '--decoder', type=str, help= "Which decoder to use kenlm or viterbi")
    parser.add_argument('-l', '--lexicon', default=None, type=str, help= "Lexicon path if decoder is kenlm")
    parser.add_argument('-L', '--lm-path', default=None, type=str, help= "Language mode path if decoder is kenlm")
    parser.add_argument('-H', '--half', default=False, type=bool, help="Half True or False")

    
    args_local = parser.parse_args()
    print("Dictionary Loaded")
    target_dict = Dictionary.load(args_local.dict)
    print("Model Loaded")
    model = get_model(args_local.cuda, args_local.model, args_local.half)
    print("Generator Loaded")
    generator = get_decoder(target_dict, args_local.decoder, args_local.lexicon, args_local.lm_path)
    
    
    cuda = args_local.cuda
    wav2vec_obj = customWav2vec(model, target_dict, generator, args_local.half)

    # run_gradio()
