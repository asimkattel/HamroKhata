#include <bitset>
#include <fstream>
#include <iostream>
#include <queue>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;

fstream ofile;
unordered_map<char, string> huffman;

class node
{
public:
    char ch;
    unsigned long long freq;
    node *l;
    node *r;
};

node *new_node(char ch, unsigned long long freq, node *l, node *r)
{
    node *n;
    n = new node();
    n->ch = ch;
    n->freq = freq;
    n->l = l;
    n->r = r;
    return n;
}

class compare
{
public:
    bool operator()(node *a, node *b)
    {
        return a->freq > b->freq;
    }
};

void encode(node *root, string str, unordered_map<char, string> &huffman)
{
    if (root == NULL)
        return;
    if (!root->l && !root->r) //leafnode;
    {
        if (str != "")
            huffman[root->ch] = str;
        else
            huffman[root->ch] = "0";
    }
    encode(root->l, str + "0", huffman);
    encode(root->r, str + "1", huffman);
}

void outp_size(unordered_map<char, unsigned long long> &freq_table)
{
    cout << freq_table['a'] << endl;
    cout << freq_table['e'] << endl;
    cout << freq_table['i'] << endl;
    cout << freq_table['o'] << endl;
    cout << freq_table['u'] << endl;
}

node *buildtree(string str)
{
    unordered_map<char, unsigned long long> freq_table;
    for (char ch : str)
    {
        freq_table[ch]++;
    }
    outp_size(freq_table);
    priority_queue<node *, vector<node *>, compare> pq;
    for (auto pair : freq_table)
    {
        if (pair.second)
            pq.push(new_node(pair.first, pair.second, NULL, NULL));
    }
    while (pq.size() > 1)
    {
        node *l = pq.top();
        pq.pop();
        node *r = pq.top();
        pq.pop();
        int sum = l->freq + r->freq;
        pq.push(new_node('\0', sum, l, r));
    }
    node *root = pq.top();
    encode(root, "", huffman);
    //for (auto pair : huffman)
    //    cout << pair.first << " " << pair.second << endl;
    string encodedstr = "";
    for (char ch : str)
    {
        encodedstr += huffman[ch];
    }
    return root;
}

string out_header(node *root, string str)
{
    if (!root)
    {
        return str;
    }
    if (!root->l && !root->r) //leaf
    {
        return str + "0" + root->ch;
    }
    str = "1" + out_header(root->l, str) + out_header(root->r, str);
    return str;
}

string transferchartobit(string str)
{
    string tmp = "";
    uint8_t a;
    for (int i = 0; i < str.size(); i++)
    {
        if (str[i] == '0')
        {
            tmp += '0';
            tmp += bitset<8>(str[i + 1]).to_string();
            str.erase(i + 1, 1);
        }
        else
        {
            tmp += str[i];
        }
    }
    return tmp;
}

string encode_string(string ori)
{
    string str = "";
    for (char ch : ori)
    {
        str += huffman[ch];
    }
    return str;
}

void pr(node *root)
{
    if (root == NULL)
        return;
    else if (!root->l && !root->r)
    {
        if (root->ch == '\n')
            cout << "\\n";
        else
            cout << root->ch;
        return;
    }
    pr(root->l);
    pr(root->r);
}

int main(int argc, char *argv[])
{
    string filename, tmp, original = "";
    fstream f;
    int i, j;
    if (argc != 2)
        return 0;
    filename.assign(argv[1]);
    f.open(filename, ios::in);
    if (!f.is_open())
        return 0;
    char cc;
    while (f.get(cc))
    {
        original += cc;
    }
    cout << original.size() << endl;
    tmp = "";
    for (i = 0; i < filename.size(); i++)
    {
        if (filename[i] == '.')
            break;
        tmp += filename[i];
    }
    ofile.open(tmp + ".compress", ios::out | ios::binary);
    node *root;
    root = buildtree(original);
    //
    //pr(root);
    //
    tmp = "";
    tmp = out_header(root, tmp);
    /*cout << endl;
    for (char cc : tmp)
    {
        if (cc == '\n')
            cout << "\\n";
        else
        {
            cout << cc;
        }
    }
    cout << endl;*/
    tmp = transferchartobit(tmp);
    //cout << tmp << endl;
    //header output
    int header_length = tmp.size();
    //cout << "header_length = " << header_length << endl;
    char l[4];
    l[0] = (header_length >> 24) % 256;
    l[1] = (header_length >> 16) % 256;
    l[2] = (header_length >> 8) % 256;
    l[3] = (header_length) % 256;
    ofile.write(l, sizeof(l));
    while (tmp.size() % 8)
    {
        tmp = tmp + "0";
    }
    char c;
    for (i = 0; i < tmp.size(); i += 8)
    {
        int t = 0;
        for (j = i; j < i + 8; j++)
        {
            t = t * 2;
            t += tmp[j] - '0';
        }
        c = t;
        ofile.put(c);
    }
    tmp = encode_string(original);
    //cout << tmp << endl;
    //file output
    int file_length = tmp.size();
    l[0] = (file_length >> 24) % 256;
    l[1] = (file_length >> 16) % 256;
    l[2] = (file_length >> 8) % 256;
    l[3] = (file_length) % 256;
    ofile.write(l, sizeof(l));
    while (tmp.size() % 8)
    {
        tmp = tmp + "0";
    }
    for (i = 0; i < tmp.size(); i += 8)
    {
        int t = 0;
        for (j = i; j < i + 8; j++)
        {
            t = t * 2;
            t += tmp[j] - '0';
        }
        c = t;
        ofile.put(c);
    }
    return 0;
}

