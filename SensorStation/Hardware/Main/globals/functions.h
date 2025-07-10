#ifndef FUNCTIONS_H
#define FUNCTIONS_H


const char* concatenate(const char* s1, const char* s2){
    size_t len1 = strlen(s1);
    size_t len2 = strlen(s2);
    size_t total = len1 + len2 + 1;

    char* result = (char*) malloc(total);
    if(!result)
        return nullptr;

    memcpy(result, s1, len1);
    memcpy(result + len1, s2, len2);
    result[total - 1] = '\0';
    return result; 
}

#endif