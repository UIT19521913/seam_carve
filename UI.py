import streamlit as st
import argparse
import time
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import pandas as pd


import seam_carving


# header

st.title("Seam Carving")

# sidebar

st.sidebar.header("Processing")

img_input = st.sidebar.file_uploader("Upload a photo", type=["png", "jpg"])

nav = st.sidebar.selectbox("Chọn thao tác muốn thực hiện", [
                           "Resize", "Remove object"])

if img_input is not None:
    # Convert the file to an opencv image.
    file_bytes = np.asarray(bytearray(img_input.read()), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)
    # Now do something with the image! For example, let's display it:
    st.image(opencv_image, channels="BGR")

    src_h, src_w, _ = opencv_image.shape
    if nav == "Resize":
        height = st.sidebar.number_input(
            "Nhập chiều cao", value=src_h, format="%d", step=2)
        width = st.sidebar.number_input(
            "Nhập chiều rộng", value=src_w, format="%d", step=2)
        button = st.sidebar.button("save")
        if button:
            st.write("Kết quả")
            dst = seam_carving.resize(opencv_image, (width, height))
            st.image(dst, channels="BGR")

    if nav == "Remove object":
        drop_mask_select = st.sidebar.checkbox("Chọn đối tượng cần xoá", True)
        drop_mask = None
        if drop_mask_select:
            st.write("Drop Mask")
            canvas_drop = st_canvas(
                # Fixed fill color with some opacity
                fill_color="rgba(255, 255, 255, .3)",
                stroke_width=1,
                stroke_color="#000000",
                background_color="#000000",
                background_image=Image.open(img_input) if img_input else None,
                update_streamlit=False,
                height=src_h,
                width=src_w,
                drawing_mode="polygon",
                display_toolbar=True,
                key="full_app_1",
            )

            if canvas_drop.image_data is not None and canvas_drop.image_data.any():
                drop_mask = np.array(
                    canvas_drop.image_data[:, :, :3], dtype=np.uint8)
                drop_mask = (drop_mask[:, :, 0] > 10) * 255
                st.image(drop_mask)

        keep_mask_select = st.sidebar.checkbox("Chọn đối tượng giữ ")
        keep_mask = None
        if keep_mask_select:
            st.write("Keep mask")
            st.write("Drop Mask")
            canvas_keep = st_canvas(
                # Fixed fill color with some opacity
                fill_color="rgba(255, 255, 255, .3)",
                stroke_width=1,
                stroke_color="#000000",
                background_color="#000000",
                background_image=Image.open(img_input) if img_input else None,
                update_streamlit=False,
                height=src_h,
                width=src_w,
                drawing_mode="polygon",
                display_toolbar=True,
                key="full_app_2",
            )

            if canvas_keep.image_data is not None and canvas_keep.image_data.any():
                keep_mask = np.array(
                    canvas_keep.image_data[:, :, :3], dtype=np.uint8)
                keep_mask = (keep_mask[:, :, 0] > 10) * 255
                st.image(keep_mask)

        confirm = st.button("Confirm")
        if confirm:
            status = st.empty()
            start = time.time()
            status.write("Performing seam carving...")

            dst = seam_carving.remove_object(
                opencv_image, drop_mask, keep_mask)
            status.write('Done at {:.4f} second(s)'.format(
                time.time() - start))
            st.image(dst, channels="BGR")
