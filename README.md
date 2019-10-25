# abpacker

ABPacker is a pattern driven sphere packer. As it is currently written, the code produces config files for the open-source event driven particle simulator [DynamO](http://dynamomd.org/). However the code could be easily modified for other uses

# Exmaple usage

```shell
$ python3
```

We can create a DynamO config using the `create_config` function

```python
>>> from abpacker import create_config
```

`create_config` allows us to specify the sphere stacking pattern in terms of the shifted sphere layer positions as described [here](https://www.nde-ed.org/EducationResources/CommunityCollege/Materials/Structure/fcc_hcp.htm)

We can create an FCC packing simulation config by calling the `create_config` function and specifying a packing pattern of `"ABC"` 

```
>>> creat_config("config.xml", 7, 1.2, "ABC")
```

Here we have specified the number of "packing cells" to be 7 as well as a simulation number density of 1.2. These packing cells consist of a single configuration of 4 particles and are shifted and layered on top of each other according to the packing pattern in order to build the simulation. The "7" means that our simulation will have 7 packing cells in both the x and y directions and double this number (14) in the z direction. The resulting simulation will have 8*7^3 particles.

We can likewise create a simulation with HCP packing by specifying a packing pattern of `"AB"` 

```
>>> creat_config("config.xml", 7, 1.2, "AB")
```
