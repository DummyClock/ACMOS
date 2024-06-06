import slack_blocks
SB = slack_blocks

# Used this to test every single function within the slack_blocks package.

block1 = SB.markdownBlock("_*~Testing markdownBlock~*_")
SB.runBlock(block1)
SB.markdownBlock("Testing *markdownBlock*'s ability to insta-run", returns=False)

block2 = SB.textBlock("Testing basic Text Block")
SB.runBlock(block2)
SB.textBlock("Testing textBlock's insta-run ability", returns=False)

blocks = [SB.dividerBlock(), SB.markdownBlock("testing the ability to run multiple blocks/passing a list of blocks"), SB.textBlock("This is a text block, previous was markdown."), SB.dividerBlock()]
SB.runBlocks(blocks)

block3 = SB.imageBlock("https://1000logos.net/wp-content/uploads/2021/04/Chick-fil-A-logo.png", "chicken place")
SB.runBlock(block3)
SB.imageBlock("https://1000logos.net/wp-content/uploads/2021/04/Chick-fil-A-logo.png", returns=False)

block4 = SB.dividerBlock()
SB.runBlock(block4)
SB.dividerBlock(returns=False)

fields = [SB.textField("Text Field")]
fields.append(SB.markdownField("*This is in a field block*"))
fields.append(SB.textField("Text Field"))
block5 = SB.fieldBlock(fields)
SB.runBlock(block5)
SB.fieldBlock(fields, returns=False)

block6 = SB.buttonBlock("Block6 Button", "block_6", "block6_button")
SB.runBlock(block6)
SB.buttonBlock("Block6 but insta-run", "iBlock6", "block6_insta",returns=False)

block7 = SB.datePicker("Block7 now", "block_7")
SB.runBlock(block7)
SB.datePicker("Block7 Insta","insta-7",returns=False)

block8 = SB.userPicker("Block8 now", "block_8")
SB.runBlock(block8)
SB.userPicker("Block8 Insta","block8_insta",returns=False)

options = [["Item 1", "item_1"], ["Item 2","item_2"], ["Item 3","item_3"]]
block9 = SB.multiselectMenu("Block9 -Multiselect", "Select an Item", options, "item_list")
SB.runBlock(block9)
SB.multiselectMenu("Block9 Insta", "Select an item", options, "block_9_insta",returns=False)
