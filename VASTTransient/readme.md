### Produce Multiwavelength webpage for VAST Transient

This code is based on either `vastpipeline` result or `vasttools` query result.

<hr>

### Basic Usage

#### `PipelineSource`

Use this class if you want to get a multiwavelength webpage based on vast-pipeline results.

```
from VASTTransient import source
pipesource = source.PipelineSource((ra, dec), measurements, images, sourcepath)
pipesource.sourceAnalysis()
```

where `measurements` is the dataframe for the measurements of the source, 
`images` is the dataframe for all images from the pipeline, 
`sourcepath` is the folder where you put all things in.

#### `VASTSource`

Use this class if you want to get a multiwavelength webpage for a random position. (You will use `vasttools` functionality)

```
from VASTTransient import source
vastsource = source.VASTSource((ra, dec), sourcepath)
vastsource.sourceAnalysis()
```

<hr>


You can view the webpage under the `sourcepath` folder
