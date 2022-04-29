# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2018. Authors: see NOTICE file.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *      http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.


__author__ = "WSH Munirah W Ahmad <wshmunirah@gmail.com>"
__copyright__ = "Apache 2 license. Made by Multimedia University Cytomine Team, Cyberjaya, Malaysia, http://cytomine.mmu.edu.my/"
__version__ = "1.0.0"

import os
import logging
import sys
import shutil

import cytomine
from cytomine import Cytomine, models, CytomineJob
from cytomine.models import Annotation, AnnotationTerm, AnnotationCollection, ImageInstanceCollection, Job, JobData, Project, ImageInstance, Property
from cytomine.models.ontology import Ontology, OntologyCollection, Term, RelationTerm, TermCollection


# Date created: 14 April 2022

def run(cyto_job, parameters):
    logging.info("----- Download analysis summary v%s -----", __version__)
    logging.info("Entering run(cyto_job=%s, parameters=%s)", cyto_job, parameters)

    job = cyto_job.job
    user = job.userJob
    project = cyto_job.project

    #Select images to process
    images = ImageInstanceCollection().fetch_with_filter("project", project.id)
    # conn.job.update(status=Job.RUNNING, progress=2, statusComment="Images gathered...")
    
    # print('images id:',images)

    list_imgs = []
    if parameters.cytomine_id_images == 'all':
        for image in images:
            list_imgs.append(int(image.id))
    else:
        list_imgs = parameters.cytomine_id_images
        list_imgs2 = list_imgs.split(',')
    
    print('Input param:', parameters.cytomine_id_images)
    # print('Print list images:', list_imgs)
    print('Print list images2:', list_imgs2)
    
    working_path = os.path.join("tmp", str(job.id))

    if not os.path.exists(working_path):
        logging.info("Creating working directory: %s", working_path)
        os.makedirs(working_path)
    try:
        output_path = os.path.join(working_path, "analysis_summary.csv")
        f= open(output_path,"w+")
        f.write("ImageID;ProjectID;JobID;TotalTerm1;TotalTerm2;TotalTerm3;TotalTerm4;TotalTerm5 \n")

        id_project=project.id
        id_job=parameters.cytomine_id_job
        id_user = parameters.cytomine_id_user
        
        #Go over images
        for id_image in list_imgs2:
            print('Current image:', id_image)

            annotations = AnnotationCollection()        
            annotations.project = id_project
            annotations.image = id_image            
            
            if parameters.id_job != 0:
                    annotations.job = id_job
                    annotations.user = id_user
                    
            annotations.showAlgo = True
            annotations.showWKT = True
            annotations.showMeta = True
            annotations.showGIS = True
            annotations.showTerm = True
            annotations.showImage = True
            annotations.annotation = True
            annotations.fetch()
            print(annotations)

       
            logging.info("Summarizing annotations for image: %s", id_image)

        # progress = 0
        # progress_delta = 100 / nb_annotations

            term1=0
            term2=0
            term3=0
            term4=0
            term5=0

            job.update(progress=20, statusComment="Analyzing annotation...")
            for i, roi in enumerate(annotations):
                
                # progress += progress_delta
                term=roi.term

                if term==[parameters.cytomine_term1]:
                    term1=term1+1                
                elif term==[parameters.cytomine_term2]:
                    term2=term2+1
                elif term==[parameters.cytomine_term3]:
                    term3=term3+1
                elif term==[parameters.cytomine_term4]:
                    term4=term4+1
                elif term==[parameters.cytomine_term5]:
                    term5=term5+1

            f.write("{};{};{};{};{};{};{};{}\n".format(id_image,id_project,job.id,term1,term2,term3,term4,term5))
            
            
        f.close() 
        job.update(progress=90, statusComment="Generating output file...")
        job_data = JobData(job.id, "Generated File", "analysis_summary.csv").save()
        job_data.upload(output_path)

    finally:
        logging.info("Deleting folder %s", working_path)
        shutil.rmtree(working_path, ignore_errors=True)
        logging.debug("Leaving run()")


if __name__ == "__main__":
    logging.debug("Command: %s", sys.argv)

    with cytomine.CytomineJob.from_cli(sys.argv) as cyto_job:
        run(cyto_job, cyto_job.parameters)


