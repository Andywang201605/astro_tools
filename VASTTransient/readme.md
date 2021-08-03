### Produce Multiwavelength webpage for VAST Transient

This code is based on either `vastpipeline` result or `vasttools` query result.

<hr>

### Basic Usage
#### `PipelineSource`

Use this class if you want to get a multiwavelength webpage based on vast-pipeline results.

```
from VASTTransient import source
pipesource = source.PipelineSource((ra, dec), measurements, images, sourcepath)
pipesource.sourceAnlysis()
```

where `measurements` is the dataframe for the measurements of the source, 
`images` is the dataframe for all images from the pipeline, 
`sourcepath` is the folder where you put all things in.

You can view the webpage under the `sourcepath` folder
