


#
# This layouter distributes space across columns.
#
def columnLayouterL2R(availableWidth:int, columnComponent):
	columnBlocks = columnComponent.columnBlocks
	nColumnGap = columnComponent.nColumnGap

	# ----

	widths = []				# the currently assigned width; initialized with minWidth
	remaining = []			# the difference between maxWidth and minWidth per component
	for b in columnBlocks:
		widths.append(b.minWidth)
		remaining.append(b.maxWidth - widths[-1])

	currentTotalWidth = sum(widths) + (len(widths) - 1) * nColumnGap	# the total width

	# expand all blocks from left to right as far as possible
	while currentTotalWidth < availableWidth:
		temp = currentTotalWidth
		for i in range(0, len(columnBlocks)):
			n = min((availableWidth - currentTotalWidth), remaining[i])
			widths[i] += n
			remaining[i] -= n
			currentTotalWidth += n
		if temp == currentTotalWidth:
			# no more changes
			break

	# now assign preferred widths and order the components to layout itself
	for i in range(0, len(columnBlocks)):
		columnBlocks[i].layout(widths[i])
#


