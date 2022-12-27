#!/usr/local/bin/python3
#
# Authors: [PLEASE PUT YOUR NAMES AND USER IDS HERE]
#
# Ice layer finder
# Based on skeleton code by D. Crandall, November 2021
#

from PIL import Image
from numpy import *
import numpy as np
from scipy.ndimage import filters
import sys
import imageio


# calculate "Edge strength map" of an image
def edge_strength(input_image):
    grayscale = array(input_image.convert('L'))
    filtered_y = zeros(grayscale.shape)
    filters.sobel(grayscale, 0, filtered_y)
    return sqrt(filtered_y ** 2)


# draw a "line" on an image (actually just plot the given y-coordinates
#  for each x-coordinate)
# - image is the image to draw on
# - y_coordinates is a list, containing the y-coordinates and length equal to the x dimension size
#   of the image
# - color is a (red, green, blue) color triple (e.g. (255, 0, 0) would be pure red
# - thickness is thickness of line in pixels
#

def column_total(edge_strength, col_no):
    col_pixels = []
    total = 0
    col_pixels = [edge_strength[row][col_no] for row in range(0, len(edge_strength))]
    total = sum(col_pixels)
    return total


def initial(image, edge_strength):
    for col in range(0, 1):
        col_pixels = [edge_strength[row][col] for row in range(0, len(edge_strength))]
        for row, pixel in enumerate(col_pixels):
            if pixel == max(col_pixels):
                return row, pixel


def initial_icerock(image, edge_strength, row_boundary):
    for col in range(0, 1):
        col_pixels = [edge_strength[row][col] for row in range(row_boundary, len(edge_strength))]
        for row, pixel in enumerate(col_pixels):
            if pixel == max(col_pixels):
                return row, pixel


def transition(curr_row, prev_row):
    if abs(curr_row - prev_row) <= 2:
        return 0.1
    else:
        return 0.001


def airice_simple_func(image, edge_strength):
    max_edge_list = []
    for col in range(0, len(edge_strength[0])):
        col_pixels = [edge_strength[row][col] for row in range(0, len(edge_strength))]
        for row, pixel in enumerate(col_pixels):
            if pixel == max(col_pixels):
                max_edge_list.append(row)
                break
    return max_edge_list


# viterbi air-ice
def airice_hmm_func(image, edge_strength):
    row_table = np.zeros((175, 224))
    prob_table = np.zeros((175, 225))
    first_col_pixels = [edge_strength[row][0] / column_total(edge_strength, 0) for row in range(0, len(edge_strength))]

    for pixel in range(len(first_col_pixels)):
        prob_table[pixel][0] = first_col_pixels[pixel]

    for col in range(224):
        for i in range(175):
            prob_list = []
            for row in range(175):
                probab = prob_table[row][col] * transition(i, row)
                prob_list.append(probab)
            max_prob = max(prob_list)
            row_final = prob_list.index(max_prob)
            prob_table[i][col + 1] = max_prob * (edge_strength[i][col + 1] / column_total(edge_strength, col + 1)) * 100
            row_table[i][col] = row_final
    last_column = list(prob_table[:, -1])
    max_value = max(last_column)
    row_number = int(last_column.index(max_value))
    row_list = []
    row_list.append(row_number)

    for col in range(223, -1, -1):
        next_row_number = int(row_table[row_number][col])
        row_list.append(next_row_number)
        row_number = next_row_number
    row_list.reverse()

    return row_list


def airice_feedback_func(image, edge_strength, gt_airice):
    airice_row = gt_airice[0]
    airice_col = gt_airice[1]
    row_table = np.zeros((175, 224))
    prob_table = np.zeros((175, 225))
    prob_table[airice_row][airice_col] = 1

    for col in range(airice_col, 224):
        for i in range(175):
            prob_list = []
            for row in range(175):
                probab = prob_table[row][col] * transition(i, row)
                prob_list.append(probab)
            max_prob = max(prob_list)
            row_final = prob_list.index(max_prob)
            prob_table[i][col + 1] = max_prob * (edge_strength[i][col + 1] / column_total(edge_strength, col + 1)) * 100
            row_table[i][col] = row_final

    for col in range(airice_col, -1, -1):
        for i in range(175):
            prob_list = []
            for row in range(175):
                probab = prob_table[row][col] * transition(i, row)
                prob_list.append(probab)
            max_prob = max(prob_list)
            row_final = prob_list.index(max_prob)
            prob_table[i][col - 1] = max_prob * (edge_strength[i][col - 1] / column_total(edge_strength, col - 1)) * 100
            row_table[i][col] = row_final
    last_column = list(prob_table[:, -1])
    max_value = max(last_column)
    row_number = int(last_column.index(max_value))
    row_list = []
    row_list.append(row_number)

    for col in range(223, -1, -1):
        next_row_number = int(row_table[row_number][col])
        row_list.append(next_row_number)
        row_number = next_row_number
    row_list.reverse()

    return row_list


# simple ice-rock boundary
def boundary_simple(image, edge_strength, col):
    simple_answer = airice_simple_func(image, edge_strength)
    ice_boundary = [x + 14 for x in simple_answer]
    return ice_boundary[col]


# viterbi ice-rock boundary
def boundary_hmm(image, edge_strength):
    viterbi_answer = airice_hmm_func(image, edge_strength)
    ice_boundary = [x + 14 for x in viterbi_answer]
    return ice_boundary


# part3 ice-rock boundary
def boundary_feedback(image, edge_strength, gt_airice):
    part3_answer = airice_feedback_func(image, edge_strength, gt_airice)
    ice_boundary = [x + 14 for x in part3_answer]
    return ice_boundary


# simple ice-rock
def icerock_simple_func(image, edge_strength):
    max_edge_list = []
    for col in range(0, len(edge_strength[0])):
        row_boundary = boundary_simple(image, edge_strength, col)
        col_pixels = [edge_strength[row][col] for row in range(row_boundary, len(edge_strength))]
        for row, pixel in enumerate(col_pixels):
            if pixel == max(col_pixels):
                max_edge_list.append(row + row_boundary)
                break
    return max_edge_list


# viterbi ice_rock
def icerock_hmm_func(image, edge_strength):
    row_table = np.zeros((175, 224))
    prob_table = np.zeros((175, 225))
    boundary_list = boundary_hmm(image, edge_strength)
    first_col_boundary = boundary_list[0]
    first_col_pixels = [edge_strength[row][0] / column_total(edge_strength, 0) for row in
                        range(first_col_boundary, 175)]
    for pixel in range(len(first_col_pixels)):
        prob_table[pixel + first_col_boundary][0] = first_col_pixels[pixel]
    for col in range(224):
        boundary_curr = boundary_list[col + 1]
        for i in range(boundary_curr, 175):
            prob_list = []
            boundary_prev = boundary_list[col]
            for row in range(boundary_prev, 175):
                probab = prob_table[row][col] * transition(i, row)
                prob_list.append(probab)
            max_prob = max(prob_list)
            row_final = prob_list.index(max_prob) + boundary_prev
            prob_table[i][col + 1] = max_prob * (edge_strength[i][col + 1] / column_total(edge_strength, col + 1)) * 100
            row_table[i][col] = row_final
    last_column = list(prob_table[:, -1])
    max_value = max(last_column)
    row_number = int(last_column.index(max_value))
    row_list = []
    row_list.append(row_number)
    for col in range(223, -1, -1):
        next_row_number = int(row_table[row_number][col])
        row_list.append(next_row_number)
        row_number = next_row_number
    row_list.reverse()
    return row_list


def icerock_feedback_func(image, edge_strength, gt_airice, gt_icerock):
    icerock_row = gt_icerock[0]
    icerock_col = gt_icerock[1]
    row_table = np.zeros((175, 224))
    prob_table = np.zeros((175, 225))

    prob_table[icerock_row][icerock_col] = 1

    boundary_list = boundary_feedback(image, edge_strength, gt_airice)

    for col in range(icerock_col, 224):
        boundary_curr = boundary_list[col + 1]
        for i in range(boundary_curr, 175):
            prob_list = []
            boundary_prev = boundary_list[col]
            for row in range(boundary_prev, 175):
                probab = prob_table[row][col] * transition(i, row)
                prob_list.append(probab)
            max_prob = max(prob_list)
            row_final = prob_list.index(max_prob) + boundary_prev
            prob_table[i][col + 1] = max_prob * (edge_strength[i][col + 1] / column_total(edge_strength, col + 1)) * 100
            row_table[i][col] = row_final

    for col in range(icerock_col, -1, -1):
        boundary_curr = boundary_list[col + 1]
        for i in range(boundary_curr, 175):
            prob_list = []
            boundary_prev = boundary_list[col]
            for row in range(boundary_prev, 175):
                probab = prob_table[row][col] * transition(i, row)
                prob_list.append(probab)
            max_prob = max(prob_list)
            row_final = prob_list.index(max_prob) + boundary_prev
            prob_table[i][col - 1] = max_prob * (edge_strength[i][col - 1] / column_total(edge_strength, col - 1)) * 100
            row_table[i][col] = row_final

    last_column = list(prob_table[:, -1])
    max_value = max(last_column)
    row_number = int(last_column.index(max_value))
    row_list = []
    row_list.append(row_number)
    for col in range(223, -1, -1):
        next_row_number = int(row_table[row_number][col])
        row_list.append(next_row_number)
        row_number = next_row_number
    row_list.reverse()

    return row_list


def draw_boundary(image, y_coordinates, color, thickness):
    for (x, y) in enumerate(y_coordinates):
        for t in range(int(max(y - int(thickness / 2), 0)), int(min(y + int(thickness / 2), image.size[1] - 1))):
            image.putpixel((x, t), color)
    return image


def draw_asterisk(image, pt, color, thickness):
    for (x, y) in [(pt[0] + dx, pt[1] + dy) for dx in range(-3, 4) for dy in range(-2, 3) if
                   dx == 0 or dy == 0 or abs(dx) == abs(dy)]:
        if 0 <= x < image.size[0] and 0 <= y < image.size[1]:
            image.putpixel((x, y), color)
    return image


# Save an image that superimposes three lines (simple, hmm, feedback) in three different colors
# (yellow, blue, red) to the filename
def write_output_image(filename, image, simple, hmm, feedback, feedback_pt):
    new_image = draw_boundary(image, simple, (255, 255, 0), 2)
    new_image = draw_boundary(new_image, hmm, (0, 0, 255), 2)
    # new_image = draw_boundary(new_image, feedback, (255, 0, 0), 2)
    # new_image = draw_asterisk(new_image, feedback_pt, (255, 0, 0), 2)
    imageio.imwrite(filename, new_image)


# main program
#
if __name__ == "__main__":

    if len(sys.argv) != 6:
        raise Exception(
            "Program needs 5 parameters: input_file airice_row_coord airice_col_coord icerock_row_coord icerock_col_coord")

    input_filename = sys.argv[1]
    airice_row_coord = sys.argv[2]
    airice_col_coord = sys.argv[3]
    icerock_row_coord = sys.argv[4]
    icerock_col_coord = sys.argv[5]

    gt_airice = [int(i) for i in sys.argv[2:4]]
    gt_icerock = [int(i) for i in sys.argv[4:6]]

    # load in image
    input_image = Image.open(input_filename).convert('RGB')
    image_array = array(input_image.convert('L'))

    # compute edge strength mask -- in case it's helpful. Feel free to use this.
    edge_strength = edge_strength(input_image)
    imageio.imwrite('edges.png', uint8(255 * edge_strength / (amax(edge_strength))))

    # You'll need to add code here to figure out the results! For now,
    # just create some random lines.
    airice_simple = airice_simple_func(input_image, edge_strength)
    airice_hmm = airice_hmm_func(input_image, edge_strength)
    airice_feedback = airice_feedback_func(input_image, edge_strength, gt_airice)

    icerock_simple = icerock_simple_func(input_image, edge_strength)
    icerock_hmm = icerock_hmm_func(input_image, edge_strength)
    icerock_feedback = icerock_feedback_func(input_image, edge_strength, gt_airice, gt_icerock)

    # Now write out the results as images and a text file
    write_output_image("air_ice_output.png", input_image, airice_simple, airice_hmm, airice_feedback, gt_airice)
    write_output_image("ice_rock_output.png", input_image, icerock_simple, icerock_hmm, icerock_feedback, gt_icerock)
    with open("layers_output.txt", "w") as fp:
        for i in (airice_simple, airice_hmm, airice_feedback, icerock_simple, icerock_hmm, icerock_feedback):
            fp.write(str(i) + "\n")

