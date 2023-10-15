def filter_llm_response(response):
    tags = ["Candidate:", "Interviewer:", "Command:", "System:"]

    # find first occurence of any in tags, then return everything after that including the tag
    tag_indices = []
    for tag in tags:
        # check if tag in response
        if tag in response:
            # get index of tag
            tag_indices.append(response.index(tag))
    
    if len(tag_indices) == 0:
        # no tag found, return everything
        return response
    
    return response[min(tag_indices):]

if __name__ == "__main__":
    test_string = """with the candidate by providing the definition of infusion from the reference information.
    Interviewer: Infusion refers to inserting the medicine directly into a patients bloodstream via IV (intravenous) application, ideally through the patient’s arm. Does this answer your question?"""

    print(filter_llm_response(test_string))