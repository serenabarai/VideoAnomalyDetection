import numpy as np


def sliding_window(arr, size, stride):
    num_chunks = int((len(arr) - size) / stride) + 2
    # print("Number of chunks",num_chunks) #110.25
    # print("Array lenght", len(arr)) #1748
    result = []
    for i in range(0,  num_chunks * stride, stride):
        if len(arr[i:i + size]) > 0:
            result.append(arr[i:i + size])
    return np.array(result)


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def interpolate(features, features_per_bag):  #features.shape = 110x4096, features_per_bag=32
    feature_size = np.array(features).shape[1]
    print("feature_size", feature_size)
    interpolated_features = np.zeros((features_per_bag, feature_size))
    interpolation_indicies = np.round(np.linspace(0, len(features) - 1, num=features_per_bag + 1))  #gives 33 equally distributed numbers between 0 and 109
    print("interpolation_indicies", interpolation_indicies)
    count = 0
    for index in range(0, len(interpolation_indicies)-1):
        start = int(interpolation_indicies[index])  #start=clip from where 'index'th video starts
        end = int(interpolation_indicies[index + 1]) #end = clip where index'th video ends

        assert end >= start

        if start == end:
            temp_vect = features[start, :]
        else:
            temp_vect = np.mean(features[start:end+1, :], axis=0)  #taking mean of all the 16frame clips within the segment

        temp_vect = temp_vect / np.linalg.norm(temp_vect)  #l2 regularisation for the features extracted

        if np.linalg.norm(temp_vect) == 0:
            print("Error")

        interpolated_features[count,:]=temp_vect
        count = count + 1

    return np.array(interpolated_features)


def extrapolate(outputs, num_frames):
    extrapolated_outputs = []
    extrapolation_indicies = np.round(np.linspace(0, len(outputs) - 1, num=num_frames))
    for index in extrapolation_indicies:
        extrapolated_outputs.append(outputs[int(index)])
    return np.array(extrapolated_outputs)


def test_interpolate():
    test_case1 = np.random.randn(24, 2048)
    output_case1 = interpolate(test_case1, 32)
    assert output_case1.shape == (32, 2048)

    test_case2 = np.random.randn(32, 2048)
    output_case2 = interpolate(test_case2, 32)
    assert output_case2.shape == (32, 2048)

    test_case3 = np.random.randn(42, 2048)
    output_case3 = interpolate(test_case3, 32)
    assert output_case3.shape == (32, 2048)

