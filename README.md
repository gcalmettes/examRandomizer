# examRandomizer
Randomize questions order, multiple choice responses order and figure versions from a LaTex file created with the [LaTex exam class](https://ctan.org/pkg/exam?lang=en).

This script allows to generate `n` different versions of an exam, by allowing the possibility to randomize:
  * the order of the questions
  * the order of the possible responses of a multiple choice questions
  * the figure(s) version(s) used in the document if several versions of the figure(s) are provided

The script also add an environment `minipage` to every question so the questions cannot be cut by a page-break. If a question has multiple-part (`parts` environment) then the `minipage` environment is added to each isolated part instead of the full question to prevent too long questions to not be displayed fully.

This repo contains a self-sufficient example, in which 10 different versions of an exam will be created:

  * The `master-file` folder contains the files needed to generate the master file of an exam created with the [exam](https://ctan.org/pkg/exam?lang=en) class of LaTex. This includes both the LaTex files, as well as the different versions of the figures that will be randomly chosen to be included in each version (in this example, there are two figures in the exam, but only one of them will be different from exam to exam).
  * The `randomization-script` folder contains the python script generating the different versions of the exam. This script also call the compilation of the generated LaTex files using `pdflatex` and save the different randomized versions of the exam in the `outputRandom` folder.
