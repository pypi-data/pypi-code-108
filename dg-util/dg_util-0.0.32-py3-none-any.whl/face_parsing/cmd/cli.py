import argparse
import glob
import os
from distutils.util import strtobool


import filetype
from tqdm import tqdm

import sys 
sys.path.append("..") 
# directory = os.getcwd()
# print(directory)
# from interfaces import parsing_face, parsing_faces
from model import BiSeNet


def parsing_face(net, image):
    import io
    to_tensor = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])
    # img=Image.open(input_path)
    image = input_img.resize((512, 512), Image.BILINEAR)
    img = to_tensor(image)
    img = torch.unsqueeze(img, 0)
    img = img.cuda()
    with torch.no_grad():
        out = net(img)[0]
    parsing = out.squeeze(0).cpu().numpy().argmax(0)

    vis_parsing_anno, vis_im = vis_parsing_maps(image, parsing, stride=1, save_im=False)
    bio = io.BytesIO()
    vis_im.save(bio, "PNG")

    return bio.getbuffer()


@parsing.command()
@parsing.argument('in_path')
@parsing.argument('out_path')
def main(in_path, out_path):
    model_path = os.environ.get(
        "U2NETP_PATH",
        os.path.expanduser(os.path.join("~", ".u2net")),
    )
    model_path='../.cache/face_parsing/79999_iter.pth'
    model=BiSeNet()
    model.load_state_dict(torch.load(model_path))
    


    r = lambda i: i.buffer.read() if hasattr(i, "buffer") else i.read()
    w = lambda o, data: o.buffer.write(data) if hasattr(o, "buffer") else o.write(data)

    if os.path.isdir(in_path):
        if os.path.isdir(out_path):
            out_folder = out_path
        else:
            out_folder = out_path.rsplit('/')[0]

        # input_paths = [full_paths[0]]
        input_paths = os.path.listdir(in_path)
        output_path = full_paths[1]

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        files = set()

        for path in input_paths:
            if os.path.isfile(path):
                files.add(path)
            else:
                input_paths += set(glob.glob(path + "/*"))

        for fi in tqdm(files):
            fi_type = filetype.guess(fi)

            if fi_type is None:
                continue
            elif fi_type.mime.find("image") < 0:
                continue

            with open(fi, "rb") as input:
                with open(
                    os.path.join(
                        output_path, os.path.splitext(os.path.basename(fi))[0] + ".png"
                    ),
                    "wb",
                ) as output:
                    w(
                        output,
                        parsing_face(
                            r(input)
                    )
                )

    else:
        if os.path.isdir(out_path):
            out_path = os.path.join(output_path, os.path.splitext(os.path.basename(in_path))[0]) + ".png"
        w(
            out_path,
            parsing_face(
                r(in_path)
            ),
        )


if __name__ == "__main__":
    main()
