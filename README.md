# examRandomizer
Randomize questions order, multiple choice responses order and figure versions from a LaTex file created with the exam class.

This script allows to generate `n` different versions of an exam, by allowing the possibility to randomize:
  * the order of the questions
  * the order of the possible responses of a multiple choice questions
  * the figure version used in the document if several versions of the figure are provided

This repo contains a self-sufficient example:

  * The `master-file` folder contains the files needed to generate the master file of an exam created with the [exam](https://ctan.org/pkg/exam?lang=en) class of LaTex. This includes both the LaTex files, as well as the different versions of the figures from which
  * The `randomization-script` folder contains the python script generating the different versions of the exam. This script also call the compilation of the generated LaTex files using `pdflatex` and save the different randomized versions of the exam in the `outputRandom` folder.
