/** \mainpage QGIS
*
*  \section about  About QGIS
* QGIS is a user friendly Open Source Geographic Information
* System (GIS) that runs on Linux, Unix, Mac OSX, and Windows. QGIS supports
* vector, raster, and database formats. QGIS is licensed under the GNU Public
* License.
*
* This API documentation provides information about all classes that make up QGIS.
*/

%ModuleHeaderCode
#include <qgis.h>
%End

%ModuleCode
  int QgisEvent = QEvent::User + 1;
%End


/** \ingroup core
 * The Qgis class provides global constants for use throughout the application.
 */
class Qgis
{
%TypeHeaderCode
#include <qgis.h>
%End

  public:
    // Version constants
    //
    // Version string
    static const QString QGIS_VERSION;
    // Version number used for comparing versions using the "Check QGIS Version" function
    static const int QGIS_VERSION_INT;
    // Release name
    static const QString QGIS_RELEASE_NAME;
    // The development version
    static const char* QGIS_DEV_VERSION;

    // Enumerations
    //

    /** Raster data types.
     *  This is modified and extended copy of GDALDataType.
     */
    enum DataType
    {
      /** Unknown or unspecified type */                UnknownDataType,
      /** Eight bit unsigned integer (quint8) */        Byte,
      /** Sixteen bit unsigned integer (quint16) */     UInt16,
      /** Sixteen bit signed integer (qint16) */        Int16,
      /** Thirty two bit unsigned integer (quint32) */  UInt32,
      /** Thirty two bit signed integer (qint32) */     Int32,
      /** Thirty two bit floating point (float) */      Float32,
      /** Sixty four bit floating point (double) */     Float64,
      /** Complex Int16 */                              CInt16,
      /** Complex Int32 */                              CInt32,
      /** Complex Float32 */                            CFloat32,
      /** Complex Float64 */                            CFloat64,
      /** Color, alpha, red, green, blue, 4 bytes the same as
          QImage::Format_ARGB32 */                      ARGB32,
      /** Color, alpha, red, green, blue, 4 bytes  the same as
          QImage::Format_ARGB32_Premultiplied */        ARGB32_Premultiplied,
    };

    //! User defined event types
    enum UserEvent
    {
      // These first two are useful for threads to alert their parent data providers

      //! The extents have been calculated by a provider of a layer
      ProviderExtentCalcEvent,

      //! The row count has been calculated by a provider of a layer
      ProviderCountCalcEvent
    };

    /** Identify search radius in mm
     *  @note added in 2.3 */
    static const double DEFAULT_SEARCH_RADIUS_MM;

    //! Default threshold between map coordinates and device coordinates for map2pixel simplification
    static const float DEFAULT_MAPTOPIXEL_THRESHOLD;

    /** Default highlight color.  The transparency is expected to only be applied to polygon
     *  fill. Lines and outlines are rendered opaque.
     *  @note added in 2.3 */
    static const QColor DEFAULT_HIGHLIGHT_COLOR;

    /** Default highlight buffer in mm.
     *  @note added in 2.3 */
    static const double DEFAULT_HIGHLIGHT_BUFFER_MM;

    /** Default highlight line/outline minimum width in mm.
     *  @note added in 2.3 */
    static const double DEFAULT_HIGHLIGHT_MIN_WIDTH_MM;

    /** Fudge factor used to compare two scales. The code is often going from scale to scale
     *  denominator. So it looses precision and, when a limit is inclusive, can lead to errors.
     *  To avoid that, use this factor instead of using <= or >=.
     * @note added in 2.15*/
    static const double SCALE_PRECISION;
};

/** Converts a string to a double in a permissive way, e.g., allowing for incorrect
 * numbers of digits between thousand separators
 * @param string string to convert
 * @param ok will be set to true if conversion was successful
 * @returns string converted to double if possible
 * @note added in version 2.9
 * @see permissiveToInt
 */
double qgsPermissiveToDouble( QString string, bool& ok );

/** Converts a string to an integer in a permissive way, e.g., allowing for incorrect
 * numbers of digits between thousand separators
 * @param string string to convert
 * @param ok will be set to true if conversion was successful
 * @returns string converted to int if possible
 * @note added in version 2.9
 * @see permissiveToDouble
 */
int qgsPermissiveToInt( QString string, bool& ok );
//! Compares two QVariant values and returns whether the first is less than the second.
//! Useful for sorting lists of variants, correctly handling sorting of the various
//! QVariant data types (such as strings, numeric values, dates and times)
//! @see qgsVariantGreaterThan()
bool qgsVariantLessThan( const QVariant& lhs, const QVariant& rhs );

//! Compares two QVariant values and returns whether the first is greater than the second.
//! Useful for sorting lists of variants, correctly handling sorting of the various
//! QVariant data types (such as strings, numeric values, dates and times)
//! @see qgsVariantLessThan()
bool qgsVariantGreaterThan( const QVariant& lhs, const QVariant& rhs );

/** Wkt string that represents a geographic coord sys
 * @note added to replace GEOWkt
 */
const QString GEOWKT;
const QString PROJECT_SCALES;

/** PROJ4 string that represents a geographic coord sys */
const QString GEOPROJ4;
/** Magic number for a geographic coord sys in POSTGIS SRID */
const long GEOSRID;
/** Magic number for a geographic coord sys in QGIS srs.db tbl_srs.srs_id */
const long GEOCRS_ID;
/** Magic number for a geographic coord sys in EpsgCrsId ID format */
const long GEO_EPSG_CRS_ID;
/** Geographic coord sys from EPSG authority */
const QString GEO_EPSG_CRS_AUTHID;
/** The length of the string "+proj=" */
const int PROJ_PREFIX_LEN;
/** The length of the string "+ellps=" */
const int ELLPS_PREFIX_LEN;
/** The length of the string "+lat_1=" */
const int LAT_PREFIX_LEN;
/** Magick number that determines whether a projection crsid is a system (srs.db)
 *  or user (~/.qgis.qgis.db) defined projection. */
const int USER_CRS_START_ID;

//! Constant that holds the string representation for "No ellips/No CRS"
const QString GEO_NONE;

//
// Constants for point symbols
//

/** Magic number that determines the default point size for point symbols */
const double DEFAULT_POINT_SIZE;
const double DEFAULT_LINE_WIDTH;

/** Default snapping tolerance for segments */
const double DEFAULT_SEGMENT_EPSILON;

/** Qgssize is used instead of size_t, because size_t is stdlib type, unknown
 *  by SIP, and it would be hard to define size_t correctly in SIP.
 *  Currently used "unsigned long long" was introduced in C++11 (2011)
 *  but it was supported already before C++11 on common platforms.
 *  "unsigned long long int" gives syntax error in SIP.
 *  KEEP IN SYNC WITH qgssize defined in SIP! */
typedef unsigned long long qgssize;

