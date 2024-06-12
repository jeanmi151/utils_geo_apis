import re
import sys

class Meta_manipulation:
    def __init__(self):
        print("do nothing")

    def add_thesaurus(metadata, title, server, thesaurus_value,
                      local_thesaurus_name):

        catalog_specific_tags = """<gmd:descriptiveKeywords>
                <gmd:MD_Keywords>
                    <gmd:keyword>
                        <gco:CharacterString>""" + thesaurus_value + """</gco:CharacterString>
                    </gmd:keyword>
                    <gmd:type>
                        <gmd:MD_KeywordTypeCode
                                codeList="http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_KeywordTypeCode"
                                codeListValue="theme"/>
                    </gmd:type>
                    <gmd:thesaurusName>
                        <gmd:CI_Citation>
                            <gmd:title>
                                <gco:CharacterString>""" + title + """</gco:CharacterString>
                            </gmd:title>
                            <gmd:date>
                                <gmd:CI_Date>
                                    <gmd:date>
                                        <gco:Date>2024-02-12</gco:Date>
                                    </gmd:date>
                                    <gmd:dateType>
                                        <gmd:CI_DateTypeCode
                                                codeList="http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#CI_DateTypeCode"
                                                codeListValue="publication"/>
                                    </gmd:dateType>
                                </gmd:CI_Date>
                            </gmd:date>
                            <gmd:identifier>
                                <gmd:MD_Identifier>
                                    <gmd:code>
                                        <gmx:Anchor xlink:href=\"""" + server + """/geonetwork/srv/api/registries/vocabularies/local.theme.""" + local_thesaurus_name + """">
                                            geonetwork.thesaurus.local.theme.""" + local_thesaurus_name + """
                                        </gmx:Anchor>
                                    </gmd:code>
                                </gmd:MD_Identifier>
                            </gmd:identifier>
                        </gmd:CI_Citation>
                    </gmd:thesaurusName>
                </gmd:MD_Keywords>
                </gmd:descriptiveKeywords>
                """

        modified_meta, status = re.subn(r"<\/gmd:descriptiveKeywords>([\w\W]+)<gmd:resourceConstraints>",
                                        r"</gmd:descriptiveKeywords>\1" + catalog_specific_tags + "<gmd:resourceConstraints>",
                                        metadata, re.M)

        return modified_meta


    def transform_metadata_for_gn(self, original_metadata, uuid, title, geoserver_link, feat_uuid, catalog_name,
                                  id_geonode, code_epsg, final_new_server):
        # test = open("822_tbeest.xml", "w")  # 813_test
        # test.write(original_metadata)
        # test.close()
        modified_meta_tmp = original_metadata
        modified_meta = modified_meta_tmp

        if self.mode_import == "Donnée":
            meta_distribution = """ <gmd:distributionInfo>
            <gmd:MD_Distribution>
                <gmd:transferOptions>
                    <gmd:MD_DigitalTransferOptions>
                        <gmd:onLine>
                            <gmd:CI_OnlineResource>
                                <gmd:linkage>
                                    <gmd:URL>https://""" + self.final_new_server + """/geoserver/ows</gmd:URL>
                                </gmd:linkage>
                                <gmd:protocol>
                                    <gco:CharacterString>OGC:WMS</gco:CharacterString>
                                </gmd:protocol>
                                <gmd:name>
                                    <gco:CharacterString>""" + geoserver_link + """</gco:CharacterString>
                                </gmd:name>
                                <gmd:description>
                                    <gco:CharacterString>""" + title + """</gco:CharacterString>
                                </gmd:description>
                            </gmd:CI_OnlineResource>
                        </gmd:onLine>
                        <gmd:onLine>
                            <gmd:CI_OnlineResource>
                                <gmd:linkage>
                                    <gmd:URL>https://""" + self.final_new_server + """/geoserver/ows</gmd:URL>
                                </gmd:linkage>
                                <gmd:protocol>
                                    <gco:CharacterString>OGC:WFS</gco:CharacterString>
                                </gmd:protocol>
                                <gmd:name>
                                    <gco:CharacterString>""" + geoserver_link + """</gco:CharacterString>
                                </gmd:name>
                                <gmd:description>
                                    <gco:CharacterString>""" + title + """</gco:CharacterString>
                                </gmd:description>
                            </gmd:CI_OnlineResource>
                        </gmd:onLine>
                    </gmd:MD_DigitalTransferOptions>
                </gmd:transferOptions>
            </gmd:MD_Distribution>
        </gmd:distributionInfo>"""
            modified_meta = re.sub(r"<gmd:distributionInfo>(\n.*)+<\/gmd:distributionInfo>", meta_distribution,
                                   modified_meta_tmp, re.M)  # .replace("\n", "\r\n")

        modified_meta_tmp = modified_meta
        modified_meta = re.sub(r"fra", "fre", modified_meta_tmp)
        # fra ==> fre
        modified_meta_tmp = modified_meta
        mdidentifier = """<gmd:edition gco:nilReason="missing">
                            <gmd:MD_Identifier>
                                 <gmd:code>
                                     <gco:CharacterString>
                                         https://""" + self.final_new_server + """/geonetwork/?uuid=""" + uuid + """
                                     </gco:CharacterString>
                                 </gmd:code>
                             </gmd:MD_Identifier>
                         </gmd:edition>"""
        modified_meta = re.sub(r'<gmd:edition gco:nilReason="missing">(\n.*)+<\/gmd:edition>', mdidentifier,
                               modified_meta_tmp, re.M)

        modified_meta_tmp = modified_meta
        modified_meta = re.sub(r"geonode:", catalog_name.lower() + ":", modified_meta_tmp)
        # aware.cirad.fr ==> cirad.prod.apps.gs-fr-prod.camptocamp.com
        modified_meta_tmp = modified_meta
        modified_meta = re.sub(self.geonode_dns, self.final_new_server, modified_meta_tmp)

        # siwtch back thumb for later update
        modified_meta_tmp = modified_meta
        modified_meta = re.sub(r"{}\/uploaded\/thumbs".format(self.final_new_server),
                               self.server + "/uploaded/thumbs", modified_meta_tmp)

        if self.mode_import == "Document":
            # switch back pdf link for later wget

            modified_meta_tmp = modified_meta
            modified_meta = re.sub(
                r"{}\/documents\/{}\/download".format(self.final_new_server, id_geonode),
                self.server + "/documents/" + id_geonode + "/download", modified_meta_tmp)
            modified_meta_tmp = modified_meta
            modified_meta = re.sub(
                r"https:\/\/cirad\.prod\.apps\.gs-fr-prod\.camptocamp\.com\/documents\/" + id_geonode + "",
                self.server + "/geonetwork/?uuid=" + uuid, modified_meta_tmp)

        modified_meta_tmp = modified_meta
        modified_meta = self.add_thesaurus(metadata=modified_meta_tmp, title="Projet " + catalog_name,
                                           server=final_new_server,
                                           thesaurus_value=catalog_name,
                                           local_thesaurus_name="projets_cirad")
        modified_meta_tmp = modified_meta
        # modified_meta = add_thesaurus(metadata=modified_meta_tmp, title="Type de métadonnée  "+catalog_name,
        #                                             server=self.final_new_server,
        #                                             thesaurus_value=self.mode_import,
        #                                             local_thesaurus_name="meta_type" )

        # add feature connected to the metadata
        if (feat_uuid):
            add_feature_xml = """    </gmd:identificationInfo>
        <gmd:contentInfo/>
        <gmd:contentInfo>
            <gmd:MD_FeatureCatalogueDescription>
                <gmd:includedWithDataset/>
                <gmd:featureCatalogueCitation uuidref=\"""" + feat_uuid + """\"
                                              xlink:title="GeoNodeFeatureCatalogue"
                                              xlink:href="https://""" + self.final_new_server + """/geonetwork/srv/fre/csw?service=CSW&amp;request=GetRecordById&amp;version=2.0.2&amp;outputSchema=http://www.isotc211.org/2005/gmd&amp;elementSetName=full&amp;id=""" + feat_uuid + """\"/>
            </gmd:MD_FeatureCatalogueDescription>
        </gmd:contentInfo>"""
            modified_meta_tmp = modified_meta
            modified_meta = re.sub(r"<\/gmd:identificationInfo>(\n.*)+<gmd:contentInfo>(\n.*)+<\/gmd:contentInfo>",
                                   add_feature_xml, modified_meta_tmp, re.M)

        # add anchor gmx at the top of the file to uncomment for older geonode
        # xmlns: gmx = "http://www.isotc211.org/2005/gmx"
        # after this xmlns:gco="http://www.isotc211.org/2005/gco"
        modified_meta_tmp = modified_meta
        modified_meta = re.sub(r'xmlns:gco="http:\/\/www.isotc211.org\/2005\/gco"',
                               'xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:gmx="http://www.isotc211.org/2005/gmx"',
                               modified_meta_tmp)

        updaterefencesystem = """<gmd:referenceSystemInfo>
         <gmd:MD_ReferenceSystem>
           <gmd:referenceSystemIdentifier>
             <gmd:RS_Identifier>
               <gmd:code>
                 <gco:CharacterString>""" + code_epsg + """</gco:CharacterString>
               </gmd:code>
               <gmd:codeSpace>
                 <gco:CharacterString>EPSG</gco:CharacterString>
               </gmd:codeSpace>
               <gmd:version>
                 <gco:CharacterString>6.11</gco:CharacterString>
               </gmd:version>
             </gmd:RS_Identifier>
           </gmd:referenceSystemIdentifier>
         </gmd:MD_ReferenceSystem>
       </gmd:referenceSystemInfo>"""
        modified_meta_tmp = modified_meta
        modified_meta = re.sub(r'<gmd:referenceSystemInfo>(\n.*)+<\/gmd:referenceSystemInfo>', updaterefencesystem,
                               modified_meta_tmp, re.M)

        # test = open("822_test.xml", "w")  # 813_test
        # test.write(modified_meta)
        # test.close()

        # <gmd:MD_ScopeCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ScopeCode" codeListValue="dataset">dataset</gmd:MD_ScopeCode>
        # become <gmd:MD_ScopeCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ScopeCode" codeListValue="map">map</gmd:MD_ScopeCode>
        # keywords : map for Cartes
        # dataset for Donnée
        # nonGeographicDataset for document

        if self.mode_import == "Document":
            new_data_tag = """<gmd:MD_ScopeCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ScopeCode" codeListValue="nonGeographicDataset">nonGeographicDataset</gmd:MD_ScopeCode>"""
        elif self.mode_import == "Carte":
            new_data_tag = """<gmd:MD_ScopeCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ScopeCode" codeListValue="map">map</gmd:MD_ScopeCode>"""

        if self.mode_import != "Donnée":
            modified_meta_tmp = modified_meta
            modified_meta = re.sub('<gmd:MD_ScopeCode codeSpace="ISOTC211/19115" codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ScopeCode" codeListValue="dataset">dataset</gmd:MD_ScopeCode>', new_data_tag,
                                   modified_meta_tmp)

        return modified_meta

    def transform_my_feature(self, meta_feat, title, description, catalog_name, list_feat_detail=[]):

        new_title = """<gmx:name>
        <gco:CharacterString>""" + title + """ Feature</gco:CharacterString>
      </gmx:name>"""
        modified_feat = re.sub(r"<gmx:name>(\n.*)+<\/gmx:name>",
                               new_title, meta_feat, re.M)
        new_description = """<gmx:scope>
        <gco:CharacterString>""" + description + """ Feature</gco:CharacterString>
      </gmx:scope>"""
        meta_feat = modified_feat
        modified_feat = re.sub(r"<gmx:scope>(\n.*)+<\/gmx:scope>",
                               new_description, meta_feat, re.M)

        meta_feat = modified_feat
        modified_feat = re.sub(r"geonode:", catalog_name.lower() + ":", meta_feat)

        #             <gco:LocalName>fid</gco:LocalName>
        #           </gfc:memberName>
        #           <gfc:definition>
        #             <gco:CharacterString>testtefste</gco:CharacterString>
        #           </gfc:definition>
        #           <gfc:memberName>

        for detail in list_feat_detail:
            new_detail = """<gfc:memberName>
                <gco:LocalName>""" + detail[0] + """</gco:LocalName>
                </gfc:memberName>
               <gfc:definition>
                 <gco:CharacterString>""" + detail[2] + """</gco:CharacterString>
               </gfc:definition>
               """
            meta_feat = modified_feat
            # print(detail[2])
            modified_feat = re.sub(
                r"<gfc:memberName>\n\s+<gco:LocalName>" + detail[0] + "<\/gco:LocalName>\n\s+<\/gfc:memberName>",
                new_detail, meta_feat, re.M)

        meta_feat = modified_feat
        modified_feat = re.sub('<gfc:featureType xlink:href="#FT-' + catalog_name.lower() + ':(.*)\/>', '', meta_feat)

        # test = open("822_feat.xml", "w")  # 813_test
        # test.write(modified_feat)
        # test.close()

        return modified_feat


if __name__ == "__main__":
    file_to_update = sys.argv[1]
    print("Will use the file " + file_to_update)

    f = open(file_to_update)
    all_file = f.read()
    f.close()

    all_file_updated = Meta_manipulation.add_thesaurus(metadata=all_file,
                                     title="DonnéeType",
                                     server="https://georchestra-127-0-1-1.traefik.me",
                                     thesaurus_value="Test",
                                     local_thesaurus_name="type_test")
    #print(modified_meta)

    test = open(file_to_update+".new", "w")
    test.write(all_file_updated)
    test.close()
