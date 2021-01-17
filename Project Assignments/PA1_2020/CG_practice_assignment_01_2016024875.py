#!/usr/bin/env python3
# -*- coding: utf-8 -*
# sample_python aims to allow seamless integration with lua.
# see examples below

import os
import sys
import pdb  # use pdb.set_trace() for debugging
import code # or use code.interact(local=dict(globals(), **locals()))  for debugging.
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image 

FAR_AWAY = sys.maxsize
LIGHT = []

class Color:
    def __init__(self, R, G, B):
        self.color=np.array([R,G,B]).astype(np.float)

    # Gamma corrects this color.
    # @param gamma the gamma value to use (2.2 is generally used).
    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma;
        self.color=np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0,1)*255).astype(np.uint8)

class View:
    def __init__(self, viewPoint, viewDir, viewUp, viewWidth, viewHeight, viewProjNormal, projDistance, intensity):
        self.viewPoint = viewPoint
        self.viewDir = viewDir
        self.viewUp = viewUp
        self.viewWidth = viewWidth
        self.viewHeight = viewHeight
        self.viewProjNormal = viewProjNormal
        self.projDistance = projDistance
        self.intensity = intensity

class Light:
    def __init__(self, position, intensity):
        self.position = position
        self.intensity = intensity

class Shader:
    def __init__(self, type_, diffuseColor, specularColor, exponent):
        self.type = type_
        self.diffuseColor = diffuseColor
        self.specularColor = specularColor
        self.exponent = exponent

class Sphere:
    def __init__(self, ref, radius, center, shader):
        self.radius = radius
        self.center = center
        self.shader = shader    # class Shader
        self.type = 'Sphere'
        self.ref = ref

class Box:
    def __init__(self, ref, minPt, maxPt, normals, shader):
        self.minPt = minPt
        self.maxPt = maxPt
        self.normals = normals
        self.shader = shader    # class Shader
        self.type = 'Box'
        self.ref = ref

# calculate normal vectors for given vertices
def getNormal(v0, v1, v2):
    direction = np.cross(v1 - v0, v2 - v0)
    d = np.sum(direction * v2)

    return np.array([direction[0], direction[1], direction[2], d])

def getNormalsForBox(minPt, maxPt):
    points = []
    normals = []

    points.append(np.array([minPt[0], minPt[1], maxPt[2]]))
    points.append(np.array([minPt[0], maxPt[1], minPt[2]]))
    points.append(np.array([maxPt[0], minPt[1], minPt[2]]))
    points.append(np.array([minPt[0], maxPt[1], maxPt[2]]))
    points.append(np.array([maxPt[0], minPt[1], maxPt[2]]))
    points.append(np.array([maxPt[0], maxPt[1], minPt[2]]))

    normals.append(getNormal(points[0], points[2], points[4]))
    normals.append(getNormal(points[1], points[2], points[5]))
    normals.append(getNormal(points[0], points[1], points[3]))
    normals.append(getNormal(points[0], points[4], points[3]))
    normals.append(getNormal(points[4], points[2], points[5]))
    normals.append(getNormal(points[3], points[5], points[1]))

    return normals

def getSphereIntersection(obj, rayDirection, viewPoint):
    global FAR_AWAY
    minDist = FAR_AWAY

    # partA = d.d
    # partB = d.p
    # partC = p.p-r^2
    
    partA = np.sum(rayDirection * rayDirection)
    partB = np.sum((viewPoint - obj.center) * rayDirection)
    partC = np.sum((viewPoint - obj.center) ** 2) - obj.radius ** 2

    if partB ** 2 - partA * partC >= 0:
        if -partB + np.sqrt(partB ** 2 - partA * partC) >= 0:
            if minDist >= (-partB + np.sqrt(partB ** 2 - partA * partC)) / partA:
                minDist = (-partB + np.sqrt(partB ** 2 - partA * partC)) / partA

        if -partB - np.sqrt(partB ** 2 - partA * partC) >= 0:
            if minDist >= (-partB - np.sqrt(partB ** 2 - partA * partC)) / partA:
                minDist = (-partB - np.sqrt(partB ** 2 - partA * partC)) / partA

    return minDist

def getBoxIntersection(obj, rayDirection, viewPoint):
    global FAR_AWAY

    flag = True
            
    # determine tx, ty, tz min and max value

    tMin = (obj.minPt[0] - viewPoint[0]) / rayDirection[0]
    tMax = (obj.maxPt[0] - viewPoint[0]) / rayDirection[0]

    tyMin = (obj.minPt[1] - viewPoint[1]) / rayDirection[1]
    tyMax = (obj.maxPt[1] - viewPoint[1]) / rayDirection[1]

    tzMin = (obj.minPt[2] - viewPoint[2]) / rayDirection[2]
    tzMax = (obj.maxPt[2] - viewPoint[2]) / rayDirection[2]

    if tMax < tMin:
        tMin, tMax = tMax, tMin

    if tyMax < tyMin:
        tyMin, tyMax = tyMax, tyMin

    if tzMax < tzMin:
        tzMin, tzMax = tzMax, tzMin

    # ray-slab intersection with t, ty (t = tx)        
    if tMin > tyMax or tyMin > tMax:
        flag = False

    # limit the boundaries (get intersection between tx and ty)
    if tMin < tyMin:
        tMin = tyMin

    if tMax > tyMax:
        tMax = tyMax
            
    # ray-slab intersection with t and tz (t = intersection of tx and ty)
    if tMin > tzMax or tzMin > tMax:
        flag = False

    if tMin < tzMin:
        tMin = tzMin

    if tMax > tzMax:
        tMax = tzMax

    if flag == True:
        return tMin

    return FAR_AWAY

def rayTrace(objList, rayDirection, viewPoint):
    global FAR_AWAY
    minDist = FAR_AWAY
    
    # closest index of object where ray intersects
    closestIdx = -1

    # count for loop to get closest object index
    cnt = 0

    for obj in objList:
        if obj.type == 'Sphere':
            tempDist = getSphereIntersection(obj, rayDirection, viewPoint)
            
        elif obj.type == 'Box':
            tempDist = getBoxIntersection(obj, rayDirection, viewPoint)
            
        if tempDist < minDist:
            minDist, closestIdx = tempDist, cnt

        cnt = cnt + 1

    return minDist, closestIdx

def getShade(objList, rayDirection, closestIdx, minDist):
    global LIGHT, FAR_AWAY, CAMERA

    R, G, B = 0, 0, 0
    v = -rayDirection * minDist
    n = np.array([0, 0, 0])

    if objList[closestIdx].type == 'Sphere':
        n = CAMERA.viewPoint + minDist * rayDirection - objList[closestIdx].center
        n = n / np.sqrt(np.sum(n * n))

    elif objList[closestIdx].type == 'Box':
        point = CAMERA.viewPoint + rayDirection * minDist
        diff = FAR_AWAY

        idx = -1
        cnt = 0

        for normal in objList[closestIdx].normals:
            if abs(np.sum(normal[0:3] * point) - normal[3]) < diff:
                diff = abs(np.sum(normal[0:3] * point) - normal[3])
                idx = cnt
            cnt = cnt + 1

        n = objList[closestIdx].normals[idx][0:3]
        n = n / np.sqrt(np.sum(n * n))

    # light
    for i in LIGHT:
        light_i = v + i.position - CAMERA.viewPoint
        light_i = light_i / np.sqrt(np.sum(light_i * light_i))

        temp, iIdx = rayTrace(objList, -light_i, i.position)
          
        if iIdx == closestIdx:
            R = R + objList[closestIdx].shader.diffuseColor[0] * i.intensity[0] * max(0, np.dot(light_i, n))
            G = G + objList[closestIdx].shader.diffuseColor[1] * i.intensity[1] * max(0, np.dot(light_i, n))
            B = B + objList[closestIdx].shader.diffuseColor[2] * i.intensity[2] * max(0, np.dot(light_i, n))
          
            if objList[closestIdx].shader.type == 'Phong':
                unitV = v / np.sqrt(np.sum(v ** 2))

                h = unitV + light_i
                h = h / np.sqrt(np.sum(h * h))

                R = R + objList[closestIdx].shader.specularColor[0] * i.intensity[0] * pow(max(0, np.dot(n, h)), objList[closestIdx].shader.exponent[0])
                G = G + objList[closestIdx].shader.specularColor[1] * i.intensity[1] * pow(max(0, np.dot(n, h)), objList[closestIdx].shader.exponent[0])
                B = B + objList[closestIdx].shader.specularColor[2] * i.intensity[2] * pow(max(0, np.dot(n, h)), objList[closestIdx].shader.exponent[0])
                    
    result = Color(R, G, B)
    result.gammaCorrect(2.2)
    return result.toUINT8()

def main():

    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    # set default values
    viewDir=np.array([0,0,-1]).astype(np.float)
    viewUp=np.array([0,1,0]).astype(np.float)
    viewProjNormal=-1*viewDir  # you can safely assume this. (no examples will use shifted perspective camera)
    viewWidth=1.0
    viewHeight=1.0
    projDistance=1.0
    intensity=np.array([1,1,1]).astype(np.float)  # how bright the light is.

    # initialize camera setting as cameraView
    global CAMERA
    CAMERA = View(0, viewDir, viewUp, viewWidth, viewHeight, viewProjNormal, projDistance, intensity)
    
    # initialize light data as light
    global LIGHT 

    # initialize object data as objList
    objList = []

    # get image size form XML file
    imgSize=np.array(root.findtext('image').split()).astype(np.int)

    # get camera setting from XML file
    for c in root.findall('camera'):
        CAMERA.viewPoint = np.array(c.findtext('viewPoint').split()).astype(np.float)
        CAMERA.viewDir = np.array(c.findtext('viewDir').split()).astype(np.float)
        CAMERA.viewUp = np.array(c.findtext('viewUp').split()).astype(np.float)
        CAMERA.viewWidth = np.array(c.findtext('viewWidth').split()).astype(np.float)
        CAMERA.viewHeight = np.array(c.findtext('viewHeight').split()).astype(np.float)
        if(c.findtext('projNormal')):
            CAMERA.viewProjNormal = np.array(c.findtext('projNormal').split()).astype(np.float)
        if(c.findtext('projDistance')):
            CAMERA.projDistance = np.array(c.findtext('projDistance').split()).astype(np.float)
        
    # get light data from XML file
    for c in root.findall('light'):
        lightPosition = np.array(c.findtext('position').split()).astype(np.float)
        lightIntensity = np.array(c.findtext('intensity').split()).astype(np.float)
        LIGHT.append(Light(lightPosition, lightIntensity))

    idx = 0

    # get shader and surface data from XML file
    for su in root.findall('surface'):
        type_su = su.get('type')

        # type-checking
        if type_su == 'Sphere':
            radius_su = np.array(su.findtext('radius')).astype(np.float)
            center_su = np.array(su.findtext('center').split()).astype(np.float)

            ref = ''

            # get current ref of sphere
            for child in su:
                if child.tag == 'shader':
                    ref = child.get('ref')

            # get shader data of ref
            for sh in root.findall('shader'):
                if sh.get('name') == ref:                    
                    type_sh = sh.get('type')
                    diffuse_sh = np.array(sh.findtext('diffuseColor').split()).astype(np.float)

                    if type_sh == 'Phong':
                        specular_sh = np.array(sh.findtext('specularColor').split()).astype(np.float)
                        exp_sh = np.array(sh.findtext('exponent').split()).astype(np.float)
                        shader = Shader(type_sh, diffuse_sh, specular_sh, exp_sh)
                    
                    elif type_sh == 'Lambertian':
                        shader = Shader(type_sh, diffuse_sh, False, False)

                    objList.append(Sphere(ref, radius_su, center_su, shader))

        elif type_su == 'Box':
            minPt_su = np.array(su.findtext('minPt').split()).astype(np.float)
            maxPt_su = np.array(su.findtext('maxPt').split()).astype(np.float)

            normals_su = getNormalsForBox(minPt_su, maxPt_su)

            ref = ''

            # get current ref of box
            for child in su:
                if child.tag == 'shader':
                    ref = child.get('ref')

            # get shader data of ref
            for sh in root.findall('shader'):
                if sh.get('name') == ref:                    
                    type_sh = sh.get('type')
                    diffuse_sh = np.array(sh.findtext('diffuseColor').split()).astype(np.float)

                    if type_sh == 'Phong':
                        specular_sh = np.array(sh.findtext('specularColor').split()).astype(np.float)
                        exp_sh = np.array(sh.findtext('exponent').split()).astype(np.float)
                        shader = Shader(type_sh, diffuse_sh, specular_sh, exp_sh)
                    
                    elif type_sh == 'Lambertian':
                        shader = Shader(type_sh, diffuse_sh, False, False)

                    objList.append(Box(ref, minPt_su, maxPt_su, normals_su, shader))

    #code.interact(local=dict(globals(), **locals()))  

    # Create an empty image
    channels=3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype=np.uint8) # height, width, channel
    img[:,:]=0

    pixel = {'x': CAMERA.viewWidth / imgSize[0], 'y': CAMERA.viewHeight / imgSize[1]}

    # determine W, U, V vector
    W = CAMERA.viewDir
    U = np.cross(W, CAMERA.viewUp)
    V = np.cross(W, U)

    unitW = W / np.sqrt(np.sum(W * W))
    unitU = U / np.sqrt(np.sum(U * U))
    unitV = V / np.sqrt(np.sum(V * V))

    # calculate pixel (0, 0)
    startVector = unitW * CAMERA.projDistance - unitU * pixel['x'] * (imgSize[0]/2 + 1/2) - unitV * pixel['y'] * (imgSize[1]/2 + 1/2)

    # use pdb.set_trace() to track down the raw data

    for x in np.arange(imgSize[0]): 
        for y in np.arange(imgSize[1]):
            rayDirection = startVector + unitU * x * pixel['x'] + unitV * y * pixel['y']
            minDist, closestIdx = rayTrace(objList, rayDirection, CAMERA.viewPoint)       

            if closestIdx == -1:
                img[y][x] = np.array([0, 0, 0])
            else:
                img[y][x] = getShade(objList, rayDirection, closestIdx, minDist)

    rawimg = Image.fromarray(img, 'RGB')
    rawimg.save(sys.argv[1]+'.png')
    
if __name__=="__main__":
    main()
