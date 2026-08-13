# Real-Time Direction of Arrival (DOA) Estimation

A real-time Direction of Arrival estimation system using a two-microphone array and cross-correlation based Time Difference of Arrival (TDOA) estimation.

## Overview

The system estimates the direction of an incoming sound source by measuring the time difference between the signals received by two microphones.

The estimated delay is obtained from the peak of the cross-correlation between the microphone signals and is converted to the angle of arrival.

## Method

The sample delay is estimated using cross-correlation:

$$
R_{xy}[k] = \sum_n x[n]y[n-k]
$$

The corresponding time delay is:

$$
\tau = \frac{k}{f_s}
$$

The direction of arrival is calculated as:

$$
\theta = \sin^{-1}\left(\frac{c\tau}{d}\right)
$$

where:

* $d$ = microphone spacing
* $c$ = speed of sound
* $f_s$ = sampling frequency
* $\tau$ = estimated time delay

## System Parameters

| Parameter             |             Value |
| --------------------- | ----------------: |
| Microphone spacing    |            6.5 cm |
| Sampling frequency    |            48 kHz |
| Speed of sound        |           347 m/s |
| Number of microphones |                 2 |
| Estimation method     | Cross-correlation |

## System Architecture

```text
Microphone 1 ──┐
               ├──> Cross-Correlation ──> TDOA ──> DOA
Microphone 2 ──┘
```

## Limitations

Performance can be affected by environmental noise, reverberation, microphone mismatch, synchronization errors, and reflections.

## Future Work

* GCC-PHAT based TDOA estimation
* Noise reduction and filtering
* Multi-microphone array for improved localization
* Real-time visualization
* FPGA/embedded implementation

## Project Report

IEEE NITK Virtual Expo:
https://ieee.nitk.ac.in/virtual_expo/report/151


