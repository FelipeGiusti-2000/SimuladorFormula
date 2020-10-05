#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <sstream>
#include <iomanip>
#define EARTH_RADIUS 6371000
#define M_PI 3.141592653589793238
#define D2R(angleDegrees) (angleDegrees * M_PI / 180.0)

/// <summary>
/// Stand in class for vector3
/// </summary>
class v3 {
public:
	//geodetic coordinates of the point
	double alt, lat, lon;
	//cartesian coordinates of the point
	double x, y, z;

	v3 () : alt{0}, lat{0}, lon{0}, x{0}, y{0}, z{0} {}

	//fills this objects (x,y,z) coordinates based on equirectangular projection
	//assuming small relative area and treating area as surface
	void equirectangular_projection(const double& meanLat) {
		this->x = EARTH_RADIUS * this->lon * cos(meanLat);
		this->y = this->alt;
		this->z = EARTH_RADIUS * this->lat;
	}

	//get lenght (module) of vector
	double lenght() const {
		return (sqrt(this->x*this->x + this->y*this->y + this->z*this->z));
	}

	//dot product between vectors [this x other]
	double dot_product(const v3& other) const {
		return this->x * other.x + this->y * other.y + this->z * other.z;
	}

	//get angle between two vectors
	double angle_between(const v3& other) const {
		return acos(this->dot_product(other) / (this->lenght() * other.lenght()));
	}

	friend std::istream& operator >> (std::istream& in, v3& v) {
		in >> v.alt;
		if (in.peek() == ';') in.ignore();
		in >> v.lat;
		if (in.peek() == ';') in.ignore();
		in >> v.lon;

		v.lat = D2R(v.lat);
		v.lon = D2R(v.lon);

		//v.x = EARTH_RADIUS * cos(v.lat) * cos(v.lon);
		//v.y = EARTH_RADIUS * cos(v.lat) * sin(v.lon);
		//v.z = EARTH_RADIUS * sin(v.lat);

		return in;
	}
	friend std::ostream& operator << (std::ostream& out, const v3& v) {
		out << std::fixed << std::setprecision(10) 
			<< v.x << "," << v.y << "," << v.z;
		return out;
	}
	v3 operator - (const v3& rhs) {
		v3 v;

		v.alt = this->alt - rhs.alt;
		v.lon = this->lon - rhs.lon;
		v.lat = this->lat - rhs.lat;

		v.x = this->x - rhs.x;
		v.y = this->y - rhs.y;
		v.z = this->z - rhs.z;

		return v;
	}
	v3& operator -= (const v3& rhs) {
		*this = *this - rhs;
		return *this;
	}
	v3 operator / (const int& rhs) {
		v3 v;
		v.x = this->x / rhs;
		v.y = this->y / rhs;
		v.z = this->z / rhs;

		return v;
	}
	v3& operator /= (const int& rhs) {
		*this = *this / rhs;
		return *this;
	}
};


int main(void) 
{
	std::ifstream myfile;
	
	std::vector<v3> coords, filtered_points;

	myfile.open("AutoX_FSAEB2019_GPSData.csv");

	if (myfile.is_open()) {

		std::cout << "starting...\n";

		v3 origin;
		std::string s;

		//read input csv file 
		//myfile.ignore();
		myfile >> origin;
		coords.push_back(origin);

		double minLat = 0, maxLat = 0, meanLat = 0;
		for (v3 v; myfile >> v;) {
			coords.push_back(v);

			//determine mean Latitude
			if (v.lat < minLat) {
				minLat = v.lat;
			}
			if (v.lat > maxLat) {
				maxLat = v.lat;
			}
		}
		myfile.close();
		meanLat = (minLat + maxLat) / 2.;vai cagar

		//Applies projection to each points and write to csv
		origin.equirectangular_projection(meanLat);

		std::cout << coords.size() << std::endl;

		std::ofstream unfilteredEqui;
		unfilteredEqui.open("unfiltered-equirectangular-projection.csv");

		if (unfilteredEqui.is_open()) {

			for (auto& v : coords) {
				v.equirectangular_projection(meanLat);
				//make first point origin (0,0,0) of the plot
				v -= origin;
				//std::cout << v << std::endl;
				unfilteredEqui << v << std::endl;
			}
			unfilteredEqui.close();
		}
		else {
			std::cout << "Couldn't Write unfiltered to file\n";
		}

		if (coords.size() > 2) 
		{
			//compares derivatives of couples of points to filter repeated/redundant/unnecessary points
			std::cout << "starting filtering" << std::endl;

			//change these to change sampling rate
			double maxLenght = 15;
			double maxAngle = D2R(40.0);

			v3 dv_old = coords[1] - coords[0];
			filtered_points.push_back(coords[0]);
			for (int i = 2, h = 1; (size_t)i + h < coords.size(); ++i) {
				v3 pre_dv = coords[(size_t)i + h] - coords[i];
				v3 dv = pre_dv / h;

				if ((dv.angle_between(dv_old) > maxAngle) || pre_dv.lenght() > maxLenght) {
					dv_old = dv;
					h = 1;
					filtered_points.push_back(coords[i]);

				}
				else {
					++h;
				}
			}
			filtered_points.push_back(coords[coords.size() - 1]);

			//WRITE FILTERED POINTS TO CSV
			std::ofstream filtered_equi;
			filtered_equi.open("filtered-equirectangular-projection.csv");
			for (const auto& v : filtered_points) {
				filtered_equi << v << std::endl;
			}
			filtered_equi.close();
		}
		else {
			std::cout << "Failed reading csv\n";
		}
	}
	else {
		std::cout << "Couldn't open file\n";
	}

	std::cout << "End of Proram" << std::endl;
	std::cout << "Unfiltered:\t" << coords.size() << "\nFiltered:\t" << filtered_points.size() << std::endl;
	std::cin.get();
	return 0;

}