"""For some raw skin, generate 1.0, 1.8 and 1.8 bedrock skins.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from sys import exit as sysexit

import layeredimage.io
from layeredimage.layeredimage import Layer, LayeredImage
from PIL import Image, UnidentifiedImageError
from waifu2x import load_models, upscale_image


def cleanImg(image: Image.Image, alphaThreshold: int = 205) -> Image.Image:
	"""Clean up semi transparent stuff when upscaling and saving with a threshold.

	Args:
		image (Image.Image): pil image to clean up
		alphaThreshold (int, optional): threshold. Defaults to 205.

	Returns:
		Image.Image: [description]
	"""
	pixdata = image.load()
	for y in range(image.size[1]):
		for x in range(image.size[0]):
			if pixdata[x, y][3] < alphaThreshold:
				image.putpixel((x, y), (0, 0, 0, 0))
			else:
				image.putpixel((x, y), pixdata[x, y][:3] + (255,))
	return image


def ver1to2(layer: Layer) -> Layer:
	"""Convert a 1.8 skin to 1.8_bedrock.

	Args:
		layer (Layer): texture layer to upscale

	Returns:
		Layer: upscaled layer
	"""
	image = layer.image.convert("RGBA")
	args = argparse.Namespace(
		gpu=-1,
		method="scale",
		noise_level=1,
		color="rgb",
		model_dir=f"{Path(__file__).resolve().parent}/models/vgg7/",
		arch="VGG7",
		scale_ratio=2,
		tta_level=8,
		tta=False,
		block_size=128,
		batch_size=16,
	)
	model = load_models(args)
	image = cleanImg(upscale_image(args, image, model["scale"]))
	return Layer(
		layer.name,
		image,
		image.size,
		(layer.offsets[0] * 2, layer.offsets[1] * 2),
		layer.opacity,
		layer.visible,
		layer.blendmode,
	)


def ver0to1(layer: Layer) -> Layer:
	"""Convert a 1.0 skin to 1.8.

	Args:
		layer (Layer): texture layer to port

	Returns:
		Layer: ported layer
	"""
	image = layer.image.convert("RGBA")
	background = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
	background.paste(image, (0, 0), image)
	leg = image.crop((0, 16, 16, 32))
	background.paste(leg, (16, 48), leg)
	arm = image.crop((40, 16, 56, 32))
	background.paste(arm, (32, 48), arm)
	return Layer(
		layer.name,
		background,
		background.size,
		(layer.offsets[0], layer.offsets[1]),
		layer.opacity,
		layer.visible,
		layer.blendmode,
	)


def ver1to0(layer: Layer) -> Layer:
	"""Convert a 1.8 skin to 1.0.

	Args:
		layer (Layer): texture layer to backport

	Returns:
		Layer: backport layer
	"""
	image = layer.image.convert("RGBA")
	background = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
	background.paste(image, (0, 0), image)
	image2 = image.crop((0, 32, 64, 64))
	background.paste(image2, (0, 16), image2)
	return Layer(
		layer.name,
		background,
		background.size,
		(layer.offsets[0], layer.offsets[1]),
		layer.opacity,
		layer.visible,
		layer.blendmode,
	)


def ver2to1(layer: Layer) -> Layer:
	"""Convert a 1.8_bedrock skin to 1.8.

	Args:
		layer (Layer): texture layer to downscale

	Returns:
		Layer: downscale layer
	"""
	image = layer.image.convert("RGBA")
	image.resize((64, 64))
	return Layer(
		layer.name,
		image,
		image.size,
		(layer.offsets[0], layer.offsets[1]),
		layer.opacity,
		layer.visible,
		layer.blendmode,
	)


def upgradeLayer(layer: Layer, target: int = 2) -> Layer | None:
	"""Layer to port or upgrade

	Args:
		layer (Layer): texture layer to act on
		target (int, optional): target version. Defaults to 2.

	Returns:
		Layer | None: Layer or None
	"""
	ver = getVer(layer)
	if ver == target:
		return layer
	if target == 2:
		if ver == 1:
			return ver1to2(layer)
		if ver == 0:
			layer = ver0to1(layer)
			return ver1to2(layer)
	if target == 1:
		if ver == 2:
			return ver2to1(layer)
		if ver == 0:
			return ver0to1(layer)
	if target == 0:
		if ver == 2:
			layer = ver2to1(layer)
			return ver1to0(layer)
		if ver == 1:
			return ver1to0(layer)
	return None


def getVer(layer: Layer) -> int:
	"""Make a guess at the version based on the layer dimensions.

	Args:
		layer (Layer): the layer

	Returns:
		int: the estimated version
	"""
	if layer.dimensions[0] > 64 and layer.dimensions[1] > 64:
		return 2
	if layer.dimensions[1] > 32:
		return 1
	return 0


def upgradeTex(layeredImage: LayeredImage, target: int = 2) -> LayeredImage:
	"""Upgrade/ port a texture

	Args:
		layeredImage (LayeredImage): represents the texture
		target (int, optional): target version. Defaults to 2.

	Returns:
		LayeredImage: upgraded texture
	"""
	versions = {0: (64, 32), 1: (64, 64), 2: (128, 128)}
	layers = []
	for layer in layeredImage.layers:
		layers.append(upgradeLayer(layer, target))
	layeredImage.layersAndGroups = layers
	layeredImage.dimensions = versions[target]
	return layeredImage


def openRawTex(filePath: str) -> LayeredImage:
	"""Open texture from a file path

	Args:
		filePath (str): path

	Raises:
		ValueError: []

	Returns:
		LayeredImage: texture
	"""
	layeredImage = None
	try:
		image = Image.open(filePath)
		layeredImage = LayeredImage([Layer("layer0", image, image.size)])
	except UnidentifiedImageError:
		try:
			layeredImage = layeredimage.io.openLayerImage(filePath)
		except ValueError:
			print("Failed")
	if layeredImage:
		return layeredImage
	raise ValueError


def dumpTex(filePath: str):
	"""For some raw skin, generate 1.0, 1.8 and 1.8 bedrock skins.

	Args:
		filePath (str): path to skin
	"""
	# Open
	layeredImage = openRawTex(filePath)

	# Write
	filePath = f"output/{filePath}"
	if not os.path.exists(filePath):
		os.makedirs(filePath)
	ver18b = upgradeTex(layeredImage, 2)
	layeredimage.io.saveLayerImage(f"{filePath}/18b.ora", ver18b)
	cleanImg(ver18b.getFlattenLayers(), 225).save(f"{filePath}/18b.png")

	ver18 = upgradeTex(layeredImage, 1)
	layeredimage.io.saveLayerImage(f"{filePath}/18.ora", ver18)
	cleanImg(ver18.getFlattenLayers(), 225).save(f"{filePath}/18.png")

	ver10 = upgradeTex(layeredImage, 0)
	layeredimage.io.saveLayerImage(f"{filePath}/10.ora", ver10)
	cleanImg(ver10.getFlattenLayers(), 225).save(f"{filePath}/10.png")


def cli():
	"""Cli entry point."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("filepath", help="Path to skin source")
	args = parser.parse_args()
	dumpTex(args.filepath)
	sysexit(0)
