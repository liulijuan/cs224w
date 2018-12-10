// ConsoleApplication2.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include<string>
#include<vector>
#include<map>
#include<iostream>
#include<fstream>
#include<sstream>
using namespace std;

static map<string, long> dictUrl;
static map<string, long> dictQuery;

bool static startsWith(string s, string sub)
{
	return s.find(sub) == 0 ? 1 : 0;
}

vector<string> static split(string s, char flag = '\t')
{
	vector<string> sv;
	istringstream iss(s);
	string temp;

	while (getline(iss, temp, flag))
	{
		sv.push_back(temp);
	}
	return sv;
}

string static trim(string s, string c)
{
	if (s.empty())
	{
		return s;
	}
	s.erase(0, s.find_first_not_of(c));
	s.erase(s.find_last_not_of(c) + 1);
	return s;
}

void static generateGraphData(string inputFileName, string outputFileName)
{
	ifstream inputFile(inputFileName, ios::binary);
	ofstream outputFile(outputFileName);

	if (!inputFile.is_open())
	{
		cout << "Error openning file";
		exit(1);
	}

	ifstream dictFile("queryDict.tsv", ios::binary);
	if(!dictFile.is_open())
	{
		cout << "Error openning dict file";
		exit(1);
	}

	while (!dictFile.eof())
	{
		string line = "";
		getline(dictFile, line);
		vector<string> seg;
		string query = "";
		seg = split(line, '\t');
		if (seg.size() >= 2)
		{
			query = seg[1];
			long id = stol(seg[0]);
			dictQuery[query] = id;
		}
	}
	dictFile.close();

	ifstream dictFile2("urlDict.tsv", ios::binary);
	if (!dictFile2.is_open())
	{
		cout << "Error openning dict file2";
		exit(1);
	}

	while (!dictFile2.eof())
	{
		string line = "";
		getline(dictFile2, line);
		vector<string> seg;
		string url = "";
		seg = split(line, '\t');
		if (seg.size() >= 2)
		{
			url = seg[1];
			url = trim(url, "\r");
			long id = stol(seg[0]);
			dictUrl[url] = id;
		}
	}
	dictFile2.close();

	int count = 0;
	int totalCount = 0;
	while (!inputFile.eof())
	{
		totalCount++;
		string line = "";
		getline(inputFile, line);
		vector<string> seg;
		string query = "";
		string url = "";
		seg=split(line, '\t');
		if (seg.size() >= 2)
		{
			query = seg[0];
			url = seg[1];
		}
		else
		{
			continue;
		}
		query = trim(query, " ");
		query = trim(query, "\t");
		url = trim(url, " ");
		url = trim(url, "\t");
		url = trim(url, "\r");

		if (dictQuery.count(query) <= 0 || dictUrl.count(url) <= 0)
		{
			continue;
		}
		else
		{
			count++;
			outputFile << to_string(dictQuery[query]) + "\t" + to_string(dictUrl[url]) + "\n";
		}
	}
	cout << "valid count: ";
	cout << count << endl;
	cout << "total count: ";
	cout << totalCount << endl;

	inputFile.close();
	outputFile.close();

}

long static appendQueryId(long startId, string filename, string outfile)
{
	map<string, long> dictQuery;
	ifstream inputFile(filename);
	ofstream outputFile(outfile);
	if (!inputFile.is_open())
	{
		cout << "Error openning file";
		exit(1);
	}

	int count = 0;
	int totalCount = 0;
	while (!inputFile.eof())
	{
		totalCount++;
		string line = "";
		getline(inputFile, line);
		vector<string> seg;
		string query = "";
		seg = split(line, '\t');
		if (seg.size() >= 1)
		{
			query = seg[0];
		}
		else
		{
			continue;
		}
		query = trim(query, " ");
		query = trim(query, "\t");
		vector<string> queryTerms=split(query, ' ');

		if (query.size() <  4 || queryTerms.size() <  2 )
		{
			continue;
		}
		if (query.size() >  80 || queryTerms.size() >  10)
		{
			continue;
		}

		if (dictQuery.count(query) <= 0)
		{
			count++;
			dictQuery[query] = startId;

			outputFile << to_string(startId) + "\t" + query + "\n";
			startId++;
		}
	}
	cout << "valid count: ";
	cout << count << endl;
	cout << "total count: ";
	cout << totalCount << endl;
	cout << "finished count: ";
	cout << startId << endl;
	inputFile.close();
	outputFile.close();

	return startId;
}

void static appendUrlId(long startId, string filename, string outfile)
{
	ifstream inputFile(filename, ios::binary);
	ofstream outputFile(outfile);
	if (!inputFile.is_open())
	{
		cout << "Error openning file";
		exit(1);
	}

	int count = 0;
	int totalCount = 0;
	while (!inputFile.eof())
	{
		totalCount++;
		string line = "";
		getline(inputFile, line);
		vector<string> seg;
		string url = "";
		seg = split(line, '\t');
		if (seg.size() >= 1)
		{
			url = seg[0];
		}
		else
		{
			continue;
		}

		url = trim(url, " ");
		url = trim(url, "\t");
		if (!(startsWith(url, "http://")==true || !startsWith(url, "https://")==true))
		{
			continue;
		}

		if (dictUrl.count(url) <= 0)
		{
			dictUrl[url] = startId;

			outputFile << to_string(startId) + "\t" + url + "\n";
			startId++;
			count++;
		}
	}
	cout << startId << endl;
	cout << "valid count: ";
	cout << count << endl;
	cout << "total count: ";
	cout << totalCount << endl;
	inputFile.close();
	outputFile.close();
}


int main()
{
	long id = appendQueryId(0, "C:\\Users\\lijuli\\Documents\\Visual Studio 2015\\Projects\\ConsoleApplication2\\Debug\\7-day-slapi-log-query-freq.tsv", "queryDict.tsv");
	appendUrlId(12000000, "C:\\Users\\lijuli\\Documents\\Visual Studio 2015\\Projects\\ConsoleApplication2\\Debug\\7-day-slapi-log-url-freq.tsv", "urlDict.tsv");
	generateGraphData("C:\\Users\\lijuli\\Documents\\Visual Studio 2015\\Projects\\ConsoleApplication2\\Debug\\7-day-slapi-log-filtered.tsv","query-url-graphdata.tsv");


    return 0;
}



