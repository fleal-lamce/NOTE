#ifndef TEXT_H
#define TEXT_H
#include <Arduino.h>
#include <cstring>


template<int SIZE> class Text{
    public:
    const int limit = (SIZE - 1);
    char buffer[SIZE];
    int index;

    Text(){
        reset();
    }

    void reset(){
        index = 0;
        buffer[0] = '\0';
    }

    const char* get(){
        const char* aux = buffer;
        return aux;
    }

    bool available() const {
        return index > 0;
    }

    void append(char c) {
        if(index >= limit)
            return;

        buffer[index++] = c;
        buffer[index] = '\0';
    }

    void concat(const char* str) {
        while(*str && index < limit)
            append(*str++);
    }

    void concat(const String& str){
        for(int i=0; i<str.length(); i++)
            append(str.charAt(i));
    }

    void print(bool breakLine=true) const {
        breakLine ? Serial.println(buffer) : Serial.print(buffer);
    }

    String toString() const {
        return String(buffer);
    }

    bool contains(const char* key) const {
        return (find(key) != -1);
    }

    void set(int pos, char value) {
        if(pos >= 0 && pos < limit)
            buffer[pos] = value;
    }

    char charAt(int pos) const {
        return (pos >= 0 && pos < index) ? buffer[pos] : '\0';
    }

    int length() const {
        return index;
    }

    int find(const char* key) const {
        const char* p = strstr(buffer, key);
        return p ? int(p - buffer) : -1;
    }

    bool blank(char c) const {
        return (c == ' ' || c == '\t' || c == '\r' || c == '\n');
    }

    Text<SIZE> substring(int start, int end) const {
        Text<SIZE> out;
        if(start < 0)   start = 0;
        if(end > index) end = index;
        
        for(int i = start; i < end; ++i) 
            out.append(buffer[i]);
        
        return out;
    }

    void strip() {
        int start = 0;
        while (start < index && blank(buffer[start]))
            start++;
        
        int end = index - 1;
        while (end >= start && blank(buffer[end]))
            end--;
        
        int newLen = end - start + 1;
        if(newLen <= 0)
            {reset(); return;}

        memmove(buffer, buffer + start, newLen);
        index = newLen;
        buffer[index] = '\0';
    }

    void replace(const char* key, const char* value) {
        const int kLen = strlen(key);
        const int vLen = strlen(value);
        char temp[SIZE];
        int tIdx = 0;
        int rIdx = 0;

        while (rIdx < index && tIdx < limit){
            const bool c1 = (kLen > 0);
            const bool c2 = (rIdx <= index - kLen);
            const bool c3 = (strncmp(buffer + rIdx, key, kLen) == 0);

            if(c1 && c2 && c3){
                for (int j = 0; j < vLen && tIdx < limit; ++j)
                    temp[tIdx++] = value[j];
                
                rIdx += kLen;
                continue;
            } 
            
            temp[tIdx++] = buffer[rIdx++];
        }

        temp[tIdx] = '\0';
        memcpy(buffer, temp, tIdx + 1);
        index = tIdx;
    }
};

#endif 
