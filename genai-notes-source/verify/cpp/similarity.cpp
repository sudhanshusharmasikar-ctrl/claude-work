#include <cmath>
#include <iostream>
#include <vector>
using namespace std;

double dot(const vector<double>& a, const vector<double>& b) {
    double s = 0;
    for (size_t i = 0; i < a.size(); i++) s += a[i] * b[i];
    return s;
}
double norm(const vector<double>& a) { return sqrt(dot(a, a)); }

double cosine(const vector<double>& a, const vector<double>& b) {
    return dot(a, b) / (norm(a) * norm(b));
}
double euclidean(const vector<double>& a, const vector<double>& b) {
    double s = 0;
    for (size_t i = 0; i < a.size(); i++) s += (a[i] - b[i]) * (a[i] - b[i]);
    return sqrt(s);
}
vector<double> normalize(vector<double> a) {
    double n = norm(a);
    for (double& x : a) x /= n;
    return a;
}

int main() {
    vector<double> shortCat = {10, 20, 30, 40};      // "I love cat"
    vector<double> longCat  = {100, 200, 300, 400};  // a long article about cats
    vector<double> dogs     = {12, 18, 33, 35};      // a short text about dogs

    cout << "cosine(shortCat, longCat) = " << cosine(shortCat, longCat) << "\n";
    cout << "cosine(shortCat, dogs)    = " << cosine(shortCat, dogs) << "\n";
    cout << "euclid(shortCat, longCat) = " << euclidean(shortCat, longCat) << "\n";
    cout << "euclid(shortCat, dogs)    = " << euclidean(shortCat, dogs) << "\n";

    vector<double> u = normalize({3, 4});
    cout << "normalize({3,4}) = {" << u[0] << ", " << u[1] << "}  length " << norm(u) << "\n";
    cout << "euclid({4,5},{6,7}) = " << euclidean({4, 5}, {6, 7}) << "\n";
}
