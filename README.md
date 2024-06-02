<h1 align="center">Posture Productivity</h1>

<div align="center">

[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/AndrewPBerg/posture-productivity)](https://github.com/AndrewPBerg/posture-productivity/issues)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-pr/AndrewPBerg/posture-productivity)
](https://github.com/AndrewPBerg/posture-productivity/pulls)
[![GitHub License](https://img.shields.io/github/license/AndrewPBerg/posture-productivity?color=teal)
](/LICENSE)

</div>

---

<p align="center"> Helps users correct posture while sitting
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Built Using](#built_using)
- [TODO](../TODO.md)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

Posture Productivity is all about helping people work better while feeling better. This application helps the user correct their posture by alerting them when their posture is outside of the set boundaries. posture boundaries can be set by the user.

In future iterations I hope to add a Pomodoro style timer that automatically takes/ends breaks based on if the user is in the frame. I also want the project to be as accessable to non-programmers as possible, so making the program a standard .exe file is also towards the top of my list.

## 🏁 Getting Started <a name = "getting_started"></a>

### Prerequisites

This repo uses Poetry for dependency managment. See [Poetry Introduction](https://python-poetry.org/docs/) to setup Poetry on your system.

### Installing

The requisite Poetry files are already located in the main branch, to get the poetry venv up and running:

#### 1. install required dependencies

``` bash
poetry install --no-root
```
#### 2. install development dependencies (Optional)
``` bash
poetry install --no-root --with dev
```
#### 3. Verify install

``` bash
poetry show
```

#### 4. Open the poetry .venv
```bash
poetry shell
```
To verify all everything is working:
```bash
python main.py
```

## ⛏️ Built Using <a name = "built_using"></a>

- [MediaPipe](https://ai.google.dev/edge/mediapipe/framework) - Posture Estimation
- [OpenCV](https://opencv.org/) - Image Processing
- [Poetry](https://python-poetry.org/) - Dependency Managment
- [PySimpleGUI](https://www.pysimplegui.com/) - GUIs

## ✍️ Author(s) <a name = "authors"></a>

- [@AndrewPBerg](https://github.com/andrewpberg) - Idea & Work


## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- [@Iapetus-11](https://github.com/iapetus-11) - Ideas, Corrections, and Code Inspiration
- [LearnOpenCV Posture Article](https://learnopencv.com/building-a-body-posture-analysis-system-using-mediapipe/) - Calculation Ideas
