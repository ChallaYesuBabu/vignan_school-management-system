def get_subjects_by_class(class_name):

    class_num = int(class_name)

    if class_num >= 1 and class_num <= 5:
        return ["Telugu", "Hindi", "English", "Maths", "EVS", "GK", "Computer"]

    elif class_num == 6 or class_num == 7:
        return ["Telugu", "Hindi", "English", "Maths", "Science", "Social"]

    elif class_num >= 8 and class_num <= 10:
        return ["Telugu", "Hindi", "English", "Maths", "NS", "PS", "Social"]

    return []