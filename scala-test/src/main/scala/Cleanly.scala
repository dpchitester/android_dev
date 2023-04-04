import java.io.Closeable

import scala.util.Failure
import scala.util.Try
import scala.util.control.NonFatal

object Cleanly {
	def apply [C <: Closeable, R](resource: => C)(f: C => R): Try[R] = 
		Try(resource).flatMap(resourceInstance => {
			try {
				val returnValue = f(resourceInstance)
				Try(resourceInstance.close()).map(_ => returnValue)
			}
			catch {
				case NonFatal(exceptionInFunction) =>
					try {
						resourceInstance.close()
						Failure(exceptionInFunction)
					}
					catch {
						case NonFatal(exceptionInClose) =>
							exceptionInFunction.addSuppressed(exceptionInClose)
							Failure(exceptionInFunction)
					}
			}
		})
}
