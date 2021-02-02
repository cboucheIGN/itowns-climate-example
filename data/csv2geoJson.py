import json

output={"type": "FeatureCollection","name": "","crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::2154" } },"features": []}

with open('liste_hauteurs_O.csv') as data:
    first=True
    for line in data:
        if (first):
            H_headers = line.replace('\n','').split(',')
            first = False
        else:
            H_values = [float(i) for i in line.replace('\n','').split(',')]

with open('lambert_O_paris_centre.csv') as data:
    first=True
    headers=[]
    for line in data:
        if (first):
            headers=line.replace('\n','').split(',')
            first=False
            print(headers)
            idX = headers.index('X')
            idY = headers.index('Y')
            idZ = headers.index('MNT')
            print(idX, idY, idZ)
        else:
            T = line.replace('\n','').split(',')
            T2 = []
            for t in T:
                if ('"' in t):
                    t = t.replace('"','')
                else:
                    t = float(t)
                T2.append(t)
            T=T2
            # on cree un point par niveau
            for j in range(len(H_headers)):
                print('level:', H_headers[j])
                # print(H_values[j])
                l = int(H_headers[j].split('_')[2])
                # print(l)
                if ('meso' in H_headers[j]):
                    # MESO
                    # on cherche la temp sous la forme THT_level
                    Source = 'THT_'+str(l)
                else:
                    # TEB
                    # on cherche la temp sous la forme TEB_Tlevel
                    Source = 'TEB_T'+str(l)
                Temp = T[headers.index(Source)]
                f = { "type": "Feature", "geometry": { "type": "Point", "coordinates": [T[idX], T[idY], T[idZ]+H_values[j]]}, "properties": { 'temp': Temp, 'source': Source}}
                output['features'].append(f)
            # for i in range(len(headers)):
            #     f['properties'][headers[i]] = T[i]
            # 

json.dump(output, open('lambert_O_paris_centre.geojson', 'w'), ensure_ascii=False, indent=4)
