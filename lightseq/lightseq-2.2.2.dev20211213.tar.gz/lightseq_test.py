import random
import numpy as np
import lightseq.inference as lsi
import tqdm


def test_diverse_beam_search():
    model = lsi.Transformer(
        "query_bidword_cuda_v2/query_bidword_transformer_cuda.0.0.1/transformer.pb", 8
    )

    # test_input = np.array([[81, 30, 49998], [52, 49998, 49998]])
    test_input = np.array([[52, 49998, 49998]])

    res = model.infer(test_input, multiple_output=True)
    print(res)


def test_math():
    model = lsi.Transformer("lightseq_math.pb", 32)

    # test_input = np.array([[81, 30, 49998], [52, 49998, 49998]])
    test_input = np.array([[2, 448, 40, 32, 205, 5, 112] for _ in range(32)])

    res = model.infer(test_input)
    print(res)


def test_xlmr():
    model = lsi.XLMR(
        "/data00/home/xiongying.taka/projects/Multilingual_Ad_Title_Generation/multilingual_title_de.hdf5",
        4,
    )
    test_input = np.array(
        [
            [1, 382, 5179, 252, 1, 2],
            [1, 41092, 3093, 1, 2, 2],
            [1, 2068, 14229, 15728, 12323, 1],
        ]
    )
    src_lang_ids = [21, 21, 21]
    trg_lang_ids = [21, 21, 21]
    res = model.infer(test_input, src_lang_ids, trg_lang_ids)
    print(res)


def test_24e6d():
    import pickle

    with open("inp.pkl", "rb") as f:
        data = pickle.load(f)

    test_input = data[:8]
    model = lsi.Transformer("transformer.hdf5", 8)

    # test_input = np.array([[81, 30, 49998], [52, 49998, 49998]])
    # test_input = np.array([[2, 448, 40, 32, 205, 5, 112] for _ in range(4)])

    res = model.infer(test_input)
    print(res)
    with open("outp.pkl", "rb") as f:
        test_out = pickle.load(f)
    print(test_out[:8])
    np.testing.assert_allclose(res[0], test_out[:8].numpy())


def test_engec():
    model = lsi.Transformer("checkpoint6.pb", 32)
    # test_input = np.array([[100, 16, 10, 205, 2143, 2]*100])

    # for _ in range(100):
    #     res = model.infer(test_input, multiple_output=True)
    #     print(res)
    while True:
        for _ in tqdm.tqdm(range(5)):
            # batch_size = random.randint(1, 32)
            # test_input = [[100, 16, 10, 205, 2143, 2]*random.randint(1, 40) for _ in range(batch_size)]
            # # test_input = [[100, 16, 10, 205, 2143, 2]*40 for _ in range(27)]
            # max_len = max(len(a) for a in test_input)
            # test_input = [a + [1]*(max_len - len(a)) for a in test_input]
            # test_input = np.array(test_input)
            # if test_input.size > 6720:
            #     continue
            test_input = np.array(
                [[np.random.randint(i, 400) for i in range(201)]] * 32
            )
            # print(test_input)
            res = model.infer(test_input, multiple_output=True)
            # if not (np.all(res[1] > -100) and np.all(res[1] < 0)):
            # # if not -100 < res[1][0] < 0:
            #     print(res)
            #     print(test_input.shape)
            #     print(res[0].shape)

        # for _ in range(5):
        test_input = np.array(
            [[100, 16, 10, 205, 2143, 2], [100, 16, 10, 205, 2143, 2]]
        )
        res = model.infer(test_input, multiple_output=True)
        # print(res)
        if not (np.all(res[1] > -100) and np.all(res[1] < 0)):
            print(res)
            print(test_input.shape)
            print(res[0].shape)


def test_qianzhou():
    model = lsi.Transformer("en2ja-plain-atag-202106021633/transformer.pb", 8)

    with open("100m_en_nll-8batch-abnormal-tokenids.txt") as f:
        data = [
            [
                int(s)
                for s in line.replace("[", "").replace("]", "").replace(",", "").split()
            ]
            for line in f.read().splitlines()
        ]
    # print(data)

    # res_first = model.infer(test_input)
    # print(res_first)

    # test_input = data[0:8]
    # test_input = [data[4]]
    test_scores = base_scores = None
    for _ in range(10):
        for i in range(len(data) // 8):
            test_input = data[i * 8 : (i + 1) * 8]
            max_len = max(len(a) for a in test_input)
            for a in test_input:
                if len(a) < max_len:
                    a.extend([46009] * (max_len - len(a)))
            # print(test_input)
            # break
            test_input = np.array(test_input)
            res = model.infer(test_input)
            if test_scores is None:
                test_scores = res[1]
            else:
                test_scores = np.concatenate((test_scores, res[1]))
        if base_scores is None:
            base_scores = test_scores
        else:
            np.testing.assert_allclose(base_scores, test_scores)
        test_scores = None


def test_wuxian():
    model = lsi.Transformer("lightseq_bart_seq2seq_3968057_5w_b4.pb", 32)

    input_ids = np.array([[0, 2839, 33458, 18764, 221, 3]], dtype=np.int)
    model.infer(input_ids, multiple_output=True)


if __name__ == "__main__":
    # test_diverse_beam_search()
    # test_math()
    # test_xlmr()
    # test_24e6d()
    # test_engec()
    # test_qianzhou()
    test_wuxian()
