import json
import re
import asyncio
import urllib.request
from urllib.error import URLError, HTTPError

file_route = input("ruta del archivo con el source:\n")
file_quality = input("Calidad a descargar:\n")

async def searchQuality( _qualityString, _jsonObj ):
    """
    Funcion encargada de validar que exista un video con la calidad deseada.
    
    Params:
        {String}  _qualityString:    cadena de texto con la calidad a buscar.
        {Json}    _jsonObj:          objeto json con todas los videos disponibles.
    Returns:
        { Json }  entryObj          objeto json con la informacion del video.
    """
    #respuesta base.
    entryObj = None
    #por cada entrada de video dentro del json.
    for entry in _jsonObj['formats']:
        #si existe una entrada con la calidad deseada.
        if ( entry['qualityLabel'] == str(_qualityString) ):
            #asignamos la entrada a la respuesta.
            entryObj = entry
    #retornamos la respuesta.
    return entryObj

async def readFile( _fileRoute ):
    """
    Funcion encargada de leer y obtener el objeto JSON con los videos disponibles
    
    Params:
        {String}  _fileRoute:    cadena de texto con la ruta del archivo a leer.
    Returns:
        { Json }  json_obj          objeto json con la informacion del video.
    """
    #variable que almacena el nombre del video.
    final_name = ''
    #variable que almacena la cadena de texto a convertir a JSON.
    final_text = ''
    #respuesta de la funcion.
    json_obj = {
        'name': '',
        'data': []
    }
    #intentamos abrir el archivo.
    try:    
        with open ( _fileRoute, 'r', encoding="utf8") as f:
            #por cada linea dentro del archivo.
            for line in f:        
                try:
                    #realizamos una busqueda para obtener los videos disponibles.
                    found = re.search('"formats":(.+?)"playbackTracking', line).group(1)
                    final_text = found[:-1]                    
                # si no existe.
                except AttributeError:
                    #nada
                    found = ''
                #intentamos obtener el nombre del video.
                try:
                    found_name = re.search('"playerOverlayVideoDetailsRenderer":(.+?)"subtitle', line).group(1)
                    final_name = found_name[:-1]
                    #si el nombre existe.
                    if ( final_name != '' ):
                        #generamos un json temporal.
                        nameobj = json.loads( str(final_name) + '}')
                        #asignamos el nombre del video a la respuesta.
                        json_obj['name'] = nameobj['title']['simpleText']
                #si no existe.
                except AttributeError:
                    #nada.
                    final_name = ''
        #cerramos el archivo.
        f.close()
        #si se encontraron videos.
        if ( final_text != '' ):
            #asignamos un json a la respuesta de la funcion.
            json_obj['data'] = json.loads( '{"formats":'+str(final_text) )
        
        #retornamos la respuesta.
        return json_obj
    #si el archivo no existe.
    except IOError as e:
        #retornamos el error.
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        return json_obj
    except:
        return json_obj
    
async def downloadFile( _url, _videoName, _videoExtension ):
    """
    Funcion encargada de descargar un video mediante una URL.
    
    Params:
        { String } _url:              direccion del video a descargar.
        { String } _videoName:        nombre que tendra el video.
        { String } _videoExtension:   extension del video.
    
    Returns:
        None.
    """
    try:
        urllib.request.urlretrieve(str(_url), str(_videoName)+'.'+str(_videoExtension))
    except HTTPError as e:
        print( e )
    except URLError as e:
        print( e )

def saveIntoFile( _json, _route ):
    """
    Funcion que genera un archivo de texto con un JSON.
    
    Params:
        {JSON}   _json:    objeto Json a escribir en el archivo.
        {String} _route:   ruta del archivo a generar.
    """
    with open(_route, 'w') as archivito:
        archivito.write(json.dumps(_json, indent=4))
    archivito.close()
    

async def main():
    #creamos una tarea para obtener el json del archivo
    task1 = asyncio.create_task(
        readFile(file_route))
    
    #obtenemos el json del archivo.
    jsonObj = await task1
    
    #si no existe
    if ( jsonObj['data'] == [] ):
        print( "Archivo dañado o inexistente")
        exit()
    
    #creamos una tarea para validar que exite la calidad del video.
    task2 = asyncio.create_task(
        searchQuality(file_quality, jsonObj['data']))
    
    #obtenemos la calidad.
    qualityEntry = await task2

    #si no existe.
    if ( qualityEntry == None ):
        print( "No se encontro la calidad especificada")
        exit()
    
    #obtenemos la extension del video.
    extension = re.search('/(.+?);', qualityEntry['mimeType']).group(1)

    #descargamos el videp.
    await downloadFile(qualityEntry['url'], jsonObj['name'], extension )



asyncio.run(main())
    
    
    
