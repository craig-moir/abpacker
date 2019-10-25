import subprocess as sp
import xml.etree.ElementTree as ET
import numpy as np
import os
from math import sqrt, ceil
from scipy.stats import maxwell

DYNAMOD = "~/dynamo/build/dynamod"

def load_xml_file(filename):
    if (filename.endswith(".bz2")):
        import bz2
        with bz2.BZ2File(filename) as f:
            return ET.parse(f)
    else:
        return ET.parse(filename)

def length_info(ET_config):
    Lx = float(ET_config.find(".Simulation/SimulationSize").get("x"))
    Ly = float(ET_config.find(".Simulation/SimulationSize").get("y"))
    Lz = float(ET_config.find(".Simulation/SimulationSize").get("z"))
    return np.array([Lx, Ly, Lz])

def call(command):
    print(command)
    sp.call(command, shell=True)

def create_sim(config_filename, C, density, pattern, temperature=1):
    print("Make sure that 2 letters in the pattern are not together i.e. \"BB\"!")
    if not 2*C % len(pattern) == 0:
        print("The length of the pattern must be set such that 2*C % len(pattern) == 0 otherwise the last layer will overlap")
        exit()
    
    dynamod_command = DYNAMOD + " -C 2 -m 0 -o {}".format(config_filename)
    call(dynamod_command)
    config = load_xml_file(config_filename)

    particle_data_tag = config.find("./ParticleData")
    particle_tags = particle_data_tag.findall("Pt")
    
    for p in range(len(particle_tags)):
        particle_data_tag.remove(particle_tags[p])
        
    def add_particle(x, _id):
        p1 = ET.Element("Pt")
        p1.set("ID", str(_id))
        x1 = ET.SubElement(p1, "P")
        x1.set("x", str(x[0]))
        x1.set("y", str(x[1]))
        x1.set("z", str(x[2]))
        v1 = ET.SubElement(p1, "V")
        v1.set("x", str(maxwell.rvs()))
        v1.set("y", str(maxwell.rvs()))
        v1.set("z", str(maxwell.rvs()))
        particle_data_tag.insert(_id, p1)

    count = 0
    particle_count = 0
    for ix in range(C):
        for iy in range(C):
            for iz in range(C*2):
                row_type = pattern[count%len(pattern)]
                print(row_type)
                count += 1

                if row_type == "A":
                    add_particle([ix*2 + 0.5, iy*sqrt(3) + 0,           iz*sqrt(2/3)], particle_count)
                    add_particle([ix*2 + 1.5, iy*sqrt(3) + 0,           iz*sqrt(2/3)], particle_count+1)
                    add_particle([ix*2 + 0  , iy*sqrt(3) + sqrt(3)/2,   iz*sqrt(2/3)], particle_count+2)
                    add_particle([ix*2 + 1  , iy*sqrt(3) + sqrt(3)/2,   iz*sqrt(2/3)], particle_count+3)
                    
                if row_type == "B":                    
                    add_particle([ix*2 + 0.5, iy*sqrt(3) + 2/sqrt(3),   iz*sqrt(2/3)], particle_count)
                    add_particle([ix*2 + 1.5, iy*sqrt(3) + 2/sqrt(3),   iz*sqrt(2/3)], particle_count+1)
                    add_particle([ix*2 + 0  , iy*sqrt(3) + sqrt(3)/6,   iz*sqrt(2/3)], particle_count+2)
                    add_particle([ix*2 + 1  , iy*sqrt(3) + sqrt(3)/6,   iz*sqrt(2/3)], particle_count+3)
                    
                if row_type == "C":
                    add_particle([ix*2 + 0.5, iy*sqrt(3) + 4/sqrt(3),   iz*sqrt(2/3)], particle_count)
                    add_particle([ix*2 + 1.5, iy*sqrt(3) + 4/sqrt(3),   iz*sqrt(2/3)], particle_count+1)
                    add_particle([ix*2 + 0  , iy*sqrt(3) + 5*sqrt(3)/6, iz*sqrt(2/3)], particle_count+2)
                    add_particle([ix*2 + 1  , iy*sqrt(3) + 5*sqrt(3)/6, iz*sqrt(2/3)], particle_count+3)
                    
                particle_count += 4

    Lx = C*2
    Ly = C*sqrt(3)
    Lz = C*2*sqrt(2/3)

    particle_data_tag = config.find("./ParticleData")    
    particle_tags = particle_data_tag.findall("Pt")

    for p in particle_tags:
        new_x = (float(p.find("P").get("x")) - Lx/2) * (sqrt(2) / density)**(1/3)
        p.find("P").set("x", str(new_x))
        new_y = (float(p.find("P").get("y")) - Ly/2) * (sqrt(2) / density)**(1/3)
        p.find("P").set("y", str(new_y))
        new_z = (float(p.find("P").get("z")) - Lz/2) * (sqrt(2) / density)**(1/3)
        p.find("P").set("z", str(new_z))

    Lx *= (sqrt(2) / density)**(1/3)
    Ly *= (sqrt(2) / density)**(1/3)
    Lz *= (sqrt(2) / density)**(1/3)

    config.find("./Simulation/SimulationSize").set("x", str(Lx))
    config.find("./Simulation/SimulationSize").set("y", str(Ly))
    config.find("./Simulation/SimulationSize").set("z", str(Lz))
    
    config.write(config_filename)

    velocity_rescale = DYNAMOD + " {} -r {} -Z -o {}".format(config_filename, temperature, config_filename)
    call(velocity_rescale)

if __name__ == "__main__":
    
    ## pattern = "ABC" -> FCC
    ## pattern = "AB" -> HCP
    create_sim("config.xml", 4, 1.2, "ABCBCBAB")
    
