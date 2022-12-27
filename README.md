Problem Statement:
1) To estimate the two boundaries using Bayes' Net
2) To estimate the two boundaries using Viterbi
3) To improve the estimate using a human feedback

Emission Probability: (Edge_strength of each pixel)/(Total Edge_strengths of that column)
Transition Probability: (0.1 if the (difference between the row of current column and the row of previous column) is less than 2), (else it is 0.01)

Solution:
1)
- In this, we calculated the emission probability of each pixel.
- Then, the maximum emission probability of each column of the image was computed and the row number of it has been saved.
- A list has been created which has all the row numbers corresponding to each column which has the maximum emission probability
- This list has been returned to the main function which then draws the boundary for each image
- To get the boundary for the ice-rock, each row of the air-ice row-list has been added by 14 to create a threshold.
- This is because, the ice-rock boundary and the air-ice boundary cannot have a difference of less than 14 rows. This gives us better results.
- The same process has been used for the ice-rock boundary only keeping the row-theshold in check, and then returning this row-list to draw the boundary

2)
- For this part, viterbi algorithm has been used
- Two tables -> probability table and row table have been created.
- The probability table is the viterbi table that stores all the probabilities of each pixel
- The row table stores all the corresponding rows for the probability table that is later used for backtracking.
- For the first column of the probability table, the initial emission probability has been computed for each pixel
- Then for the next column, for each pixel, the transition from each pixel on the previous column to the current pixel has been computed and then multiplied with the initial probability of that pixel.
- The max of these probabilities have been taken, multiplied with the emission probability and then set to that pixel.
(Viterbi Probability = Initial Probability * Emission Probability * Transition Probability)
- The row number corresponding to the probability has been stored in the row_table.
- This way, we fill the probability table as well as the row-table
- Finally, the max value of the last column of the probability table has been taken, the corresponding row number found on the row-table and then backtracked till the first column
- The row numbers found during the backtracking have been stored in a list
- This list of row-numbers is the final list that is then used to draw the boundary of the airice
- For the ice-rock boundary, the same process has been used just keeping in mind the row threshold
- The row threshold of the ice-rock boundary compared to the airice boundary has been kept as 14

3)
- In this part, a feedback has been taken from the human
- A row and column number for both airice and icerock line has been taken as input
- This input is used to improve the previous viterbi model
- For example if the input row and column number is 20,20: The probability at [20,20] in the probability table has been set to 1, and the rest of that column has only 0 probabilities.
- This ensures that only that pixel gets selected when taken a max
- Now, using that column, the probability table has been created both in the forward direction and the backward direction using column number 20(example)
- Once the probability table is created in such a way, the row-table is used to backtrack
- This gives us better results since we have some human feedback
- For the icerock boundary, the previous steps are followed just keeping the row threshold in mind.
- The row difference between the airice boundary and the icerock boundary is kept more than 14.

These give us all the needed boundary lines which are then drawn on the image.



