#include <bitset>
#include <fstream>
#include <iostream>
#include <queue>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;

fstream in, out;
string header, ffile;

class node
{
public:
    char ch;
    node *l;
    node *r;
};

node *new_node(char ch)
{
    node *n;
    n = new node();
    n->ch = ch;
    n->l = NULL;
    n->r = NULL;
    return n;
}

string inheader(int bit)
{
    string str = "";
    int i, j, byte;
    if (bit % 8)
        byte = bit / 8 + 1;
    else
        byte = bit / 8;
    char buffer;
    int tmp;
    for (i = 0; i < byte; i++)
    {
        in.read(&buffer, sizeof(char));
        tmp = buffer;
        for (j = 7; j >= 0; j--)
        {
            if ((tmp >> j) & 1)
                str += "1";
            else
                str += "0";
        }
    }
    while (str.size() != bit)
    {
        str.pop_back();
    }
    return str;
}

string transferbit2char(string header)
{
    string str = "";
    int i, j;
    for (i = 0; i < header.size(); i++)
    {
        if (header[i] == '1')
            str += '1';
        else //header[i] == '0'
        {
            str += '0';
            uint8_t buffer = 0;
            for (char c : header.substr(i + 1, 8))
            {
                buffer = (buffer << 1) | (c - '0');
            }
            i += 8;
            str += (char)buffer;
        }
    }
    return str;
}

node *rebuild_tree(string &str)
{
    node *root;
    if (str.empty())
        return NULL;
    if (str[0] == '0')
    {
        str.erase(str.begin());
        root = new_node(str[0]);
        str.erase(str.begin());
    }
    else if (str[0] == '1')
    {
        str.erase(str.begin());
        root = new_node('\0');
        root->l = rebuild_tree(str);
        root->r = rebuild_tree(str);
    }
    return root;
}

int pos;

void foutput(node *root)
{
    if (!root)
        return;
    if (!root->l && !root->r)
    {
        if (root->ch != '\r')
            out << root->ch;
        return;
    }
    pos++;
    if (ffile.at(pos) == '0')
    {
        foutput(root->l);
    }
    else
    {
        foutput(root->r);
    }
}

int main(int argc, char *argv[])
{
    string filename;
    if (argc != 2)
        return 0;
    filename = argv[1];
    in.open(filename, ios::in | ios::binary);
    int header_length, file_length;
    char l[4];
    unsigned long long t1, t2, t3, t4;
    in.read(l, sizeof(l));
    t1 = (uint8_t)l[0], t1 = t1 << 24;
    t2 = (uint8_t)l[1], t2 = t2 << 16;
    t3 = (uint8_t)l[2], t3 = t3 << 8;
    t4 = (uint8_t)l[3];
    header_length = t1 + t2 + t3 + t4;
    //cout << header_length << endl;
    header = inheader(header_length);
    //cout << header << endl;
    header = transferbit2char(header);
    //cout << header << endl;
    node *root = rebuild_tree(header);
    //header done
    in.read(l, sizeof(l));
    t1 = (uint8_t)l[0], t1 = t1 << 24;
    t2 = (uint8_t)l[1], t2 = t2 << 16;
    t3 = (uint8_t)l[2], t3 = t3 << 8;
    t4 = (uint8_t)l[3];
    file_length = t1 + t2 + t3 + t4;
    ffile = inheader(file_length);
    filename = filename.substr(0, filename.find('.')) + "_decompressed.txt"; //!!!
    out.open(filename, ios::out);
    pos = -1;
    int prepos = -1;
    while (1)
    {
        if (pos > (int)(ffile.size()) - 2)
            break;
        foutput(root);
        if (pos == prepos)
            pos++;
        prepos = pos;
    }
    return 0;
}