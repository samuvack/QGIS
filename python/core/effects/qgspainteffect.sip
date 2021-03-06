/** \ingroup core
 * \class QgsPaintEffect
 * \brief Base class for visual effects which can be applied to QPicture drawings
 *
 * QgsPaintEffect objects can be used to modify QPicture drawings prior to rendering
 * them with a QPainter operation. There are two methods for drawing using an effect,
 * either drawing a picture directly, or by intercepting drawing operations to a
 * render context.
 *
 * To directly draw a picture, use the @link render @endlink method with a source
 * QPicture and destination render context.
 *
 * Intercepting drawing operations to a render context is achieved by first calling
 * the @link begin @endlink method, passing a render context. Any drawing operations
 * performed on the render context will not directly affect the context's paint
 * device. When the drawing operations have been completed, call the @link end @endlink
 * method. This will perform the paint effect on the intercepted drawing operations
 * and render the result to the render context's paint device.
 *
 * \see QgsPaintEffectRegistry
 * \note Added in version 2.9
 */

class QgsPaintEffect
{
%TypeHeaderCode
#include <qgspainteffect.h>
%End

%ConvertToSubClassCode
  if (sipCpp->type() == "drawSource" && dynamic_cast<QgsDrawSourceEffect*>(sipCpp) != NULL)
  {
     sipType = sipType_QgsDrawSourceEffect;
  }
  else if (sipCpp->type() == "effectStack" && dynamic_cast<QgsEffectStack*>(sipCpp) != NULL)
  {
     sipType = sipType_QgsEffectStack;
  }
  else if (sipCpp->type() == "blur" && dynamic_cast<QgsBlurEffect*>(sipCpp) != NULL)
  {
     sipType = sipType_QgsBlurEffect;
  }
  else if (sipCpp->type() == "dropShadow" && dynamic_cast<QgsDropShadowEffect*>(sipCpp) != NULL)
  {
     sipType = sipType_QgsDropShadowEffect;
  }
  else if (sipCpp->type() == "outerGlow" && dynamic_cast<QgsOuterGlowEffect*>(sipCpp) != NULL)
  {
     sipType = sipType_QgsOuterGlowEffect;
  }
  else if (sipCpp->type() == "innerGlow" && dynamic_cast<QgsInnerGlowEffect*>(sipCpp) != NULL)
  {
     sipType = sipType_QgsInnerGlowEffect;
  }
  else if (sipCpp->type() == "transform" && dynamic_cast<QgsTransformEffect*>(sipCpp) != NULL)
  {
     sipType = sipType_QgsTransformEffect;
  }
  else if (sipCpp->type() == "color" && dynamic_cast<QgsColorEffect*>(sipCpp) != NULL)
  {
     sipType = sipType_QgsColorEffect;
  }
  else
  {
    sipType = 0;
  }
%End

  public:

    /** Drawing modes for effects. These modes are used only when effects are
     * drawn as part of an effects stack
     * @see QgsEffectStack
     */
    enum DrawMode
    {
      Modifier, /*!< the result of the effect is not rendered, but is passed on to following effects in the stack */
      Render, /*!< the result of the effect is rendered on the destination, but does not affect subsequent effects in the stack */
      ModifyAndRender /*!< the result of the effect is both rendered and passed on to subsequent effects in the stack */
    };

    QgsPaintEffect();
    QgsPaintEffect( const QgsPaintEffect& other );
    virtual ~QgsPaintEffect();

    /** Returns the effect type.
     * @returns unique string representation of the effect type
     */
    virtual QString type() const = 0;

    /** Duplicates an effect by creating a deep copy of the effect
     * @returns clone of paint effect
     */
    virtual QgsPaintEffect* clone() const = 0 /Factory/;

    /** Returns the properties describing the paint effect encoded in a
     * string format.
     * @returns string map of properties, in the form property key, value
     * @see readProperties
     * @see saveProperties
     */
    virtual QgsStringMap properties() const = 0;

    /** Reads a string map of an effect's properties and restores the effect
     * to the state described by the properties map.
     * @param props effect properties encoded in a string map
     * @see properties
     */
    virtual void readProperties( const QgsStringMap& props ) = 0;

    /** Saves the current state of the effect to a DOM element. The default
     * behavior is to save the properties string map returned by
     * @link properties @endlink.
     * @param doc destination DOM document
     * @param element destination DOM element
     * @returns true if save was successful
     * @see readProperties
     */
    virtual bool saveProperties( QDomDocument& doc, QDomElement& element ) const;

    /** Restores the effect to the state described by a DOM element.
     * @param element DOM element describing an effect's state
     * @returns true if read was successful
     * @see saveProperties
     */
    virtual bool readProperties( const QDomElement& element );

    /** Renders a picture using the effect.
     * @param picture source QPicture to render
     * @param context destination render context
     * @see begin
     */
    virtual void render( QPicture& picture, QgsRenderContext& context );

    /** Begins intercepting paint operations to a render context. When the corresponding
     * @link end @endlink member is called all intercepted paint operations will be
     * drawn to the render context after being modified by the effect.
     * @param context destination render context
     * @see end
     * @see render
     */
    virtual void begin( QgsRenderContext& context );

    /** Ends interception of paint operations to a render context, and draws the result
     * to the render context after being modified by the effect.
     * @param context destination render context
     * @see begin
     */
    virtual void end( QgsRenderContext& context );

    /** Returns whether the effect is enabled
     * @returns true if effect is enabled
     * @see setEnabled
     */
    bool enabled() const;

    /** Sets whether the effect is enabled
     * @param enabled set to false to disable the effect
     * @see enabled
     */
    void setEnabled( const bool enabled );

    /** Returns the draw mode for the effect. This property only has an
     * effect if the paint effect is used in a @link QgsEffectStack @endlink
     * @returns draw mode for effect
     * @see setDrawMode
     */
    DrawMode drawMode() const;

    /** Sets the draw mode for the effect. This property only has an
     * effect if the paint effect is used in a @link QgsEffectStack @endlink
     * @param drawMode draw mode for effect
     * @see drawMode
     */
    void setDrawMode( const DrawMode drawMode );

  protected:

    /** Handles drawing of the effect's result on to the specified render context.
     * Derived classes must reimplement this method to apply any transformations to
     * the source QPicture and draw the result using the context's painter.
     * @param context destination render context
     * @see drawSource
     */
    virtual void draw( QgsRenderContext& context ) = 0;

    /** Draws the source QPicture onto the specified painter. Handles scaling of the picture
     * to account for the destination painter's DPI.
     * @param painter destination painter
     * @see source
     * @see sourceAsImage
     */
    void drawSource( QPainter& painter );

    /** Returns the source QPicture. The @link draw @endlink member can utilise this when
     * drawing the effect.
     * @returns source QPicture
     * @see drawSource
     * @see sourceAsImage
     */
    const QPicture* source() const;

    /** Returns the source QPicture rendered to a new QImage. The @link draw @endlink member can
     * utilise this when drawing the effect. The image will be padded or cropped from the original
     * source QPicture by the results of the @link boundingRect @endlink method.
     * The result is cached to speed up subsequent calls to sourceAsImage.
     * @returns source QPicture rendered to an image
     * @see drawSource
     * @see source
     * @see imageOffset
     * @see boundingRect
     */
    QImage* sourceAsImage( QgsRenderContext &context );

    /** Returns the offset which should be used when drawing the source image on to a destination
     * render context.
     * @param context destination render context
     * @returns point offset for image top left corner
     * @see sourceAsImage
     */
    QPointF imageOffset( const QgsRenderContext& context ) const;

    /** Returns the bounding rect required for drawing the effect. This method can be used
     * to expand the bounding rect of a source picture to account for offset or blurring
     * effects.
     * @param rect original source bounding rect
     * @param context destination render context
     * @returns modified bounding rect
     * @see sourceAsImage
     */
    virtual QRectF boundingRect( const QRectF& rect, const QgsRenderContext& context ) const;

    /** Applies a workaround to a QPainter to avoid an issue with incorrect scaling
     * when drawing QPictures. This may need to be called by derived classes prior
     * to rendering results onto a painter.
     * @param painter destination painter
     */
    void fixQPictureDpi( QPainter* painter ) const;

};

/** \ingroup core
 * \class QgsDrawSourceEffect
 * \brief A paint effect which draws the source picture with minor or no alterations
 *
 * The draw source effect can be used to draw an unaltered copy of the original source
 * picture. Minor changes like lowering the opacity and applying a blend mode are
 * supported, however these changes will force the resultant output to be rasterized.
 * If no alterations are performed then the original picture will be rendered as a vector.
 *
 * \note Added in version 2.9
 */

class QgsDrawSourceEffect : QgsPaintEffect
{
%TypeHeaderCode
#include <qgspainteffect.h>
%End

  public:

    QgsDrawSourceEffect();
    virtual ~QgsDrawSourceEffect();

    /** Creates a new QgsDrawSource effect from a properties string map.
     * @param map encoded properties string map
     * @returns new QgsDrawSourceEffect
     */
    static QgsPaintEffect* create( const QgsStringMap& map ) /Factory/;

    virtual QString type() const;
    virtual QgsDrawSourceEffect* clone() const /Factory/;
    virtual QgsStringMap properties() const;
    virtual void readProperties( const QgsStringMap& props );

    /** Sets the transparency for the effect
     * @param transparency double between 0 and 1 inclusive, where 0 is fully opaque
     * and 1 is fully transparent
     * @see transparency
     */
    void setTransparency( const double transparency );

    /** Returns the transparency for the effect
     * @returns transparency value between 0 and 1 inclusive, where 0 is fully opaque
     * and 1 is fully transparent
     * @see setTransparency
     */
    double transparency() const;

    /** Sets the blend mode for the effect
     * @param mode blend mode used for drawing the source on to a destination
     * paint device
     * @see blendMode
     */
    void setBlendMode( const QPainter::CompositionMode mode );

    /** Returns the blend mode for the effect
     * @returns blend mode used for drawing the source on to a destination
     * paint device
     * @see setBlendMode
     */
    QPainter::CompositionMode blendMode() const;

  protected:

    virtual void draw( QgsRenderContext& context );

};

class QgsEffectPainter
{
%TypeHeaderCode
#include <qgspainteffect.h>
%End
  public:

    /**
     * QgsEffectPainter constructor
     *
     * @param renderContext the QgsRenderContext object
     * @note Added in QGIS 3.0
     */
    QgsEffectPainter( QgsRenderContext& renderContext );

    /**
     * QgsEffectPainter constructor alternative if no painter translation is needed
     *
     * @param renderContext the QgsRenderContext object
     * @param effect the QgsPaintEffect object
     * @note Added in QGIS 3.0
     */
    QgsEffectPainter( QgsRenderContext& renderContext, QgsPaintEffect* effect );
    ~QgsEffectPainter();

    /**
     * Sets the effect to be painted
     *
     * @param effect the QgsPaintEffect object
     */
    void setEffect( QgsPaintEffect* effect );
};
